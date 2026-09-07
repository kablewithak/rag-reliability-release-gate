from __future__ import annotations

import pytest

from rag_reliability.corpus.authored_renderer import (
    ConstrainedAuthoredRenderer,
    RenderContractError,
    RenderErrorCode,
    count_active_unresolved_directives,
)
from rag_reliability.corpus.render_policy import (
    ApiVersionRow,
    ConditionalDecision,
    Phase3bRenderPolicyFreeze,
    TemplateBinding,
)


def _policy() -> Phase3bRenderPolicyFreeze:
    expressions = (
        ("elsif:ghes", False),
        ('if:query.apiVersion == nil or "2022-11-28" <= query.apiVersion', True),
        ('if:query.apiVersion == nil or "2026-03-10" <= query.apiVersion', True),
        ("ifversion:api-insights", False),
        ("ifversion:enterprise-installed-apps", False),
        ("ifversion:fpt", True),
        ("ifversion:fpt or ghec", True),
        ("ifversion:ghec", False),
        ("ifversion:ghec or ghes", False),
        ("ifversion:ghes", False),
        ("ifversion:ghes = 3.21", False),
        ("ifversion:ghes = 3.22", False),
        ("ifversion:not fpt", False),
    )
    return Phase3bRenderPolicyFreeze(
        policy_version="phase3b-render-policy-freeze-v1",
        snapshot_id="github_rest_v1_2026_09_05",
        github_docs_commit_sha="ec3629a841129ae28189d7bb2274a7b3d40c5095",
        source_dependency_manifest_sha256=(
            "508fdf53bde20072b142babd78b9d707c90b3d10eb039f3cd65cba1ebbf5a51c"
        ),
        source_render_context_review_sha256=(
            "31ad31fa06987d85960de7627a38ca6d02bd9aa4c6fb18127106a2b26f7e7369"
        ),
        source_render_semantics_review_sha256=(
            "25cae92b748ec1e40674c6813772c2c258b366e47f702da682b00dc0fd912368"
        ),
        api_version_rows=(
            ApiVersionRow(api_version="2026-03-10", end_of_support="Not yet scheduled"),
            ApiVersionRow(api_version="2022-11-28", end_of_support="March 10, 2028"),
        ),
        conditional_decisions=tuple(
            ConditionalDecision(expression=expression, result=result)
            for expression, result in expressions
        ),
        assignment_expression=(
            "versionData = tables.rest-api-versions.versions[apiVersion]"
        ),
        iteration_expression=(
            "apiVersion in allVersions[currentVersion].apiVersions"
        ),
        template_bindings=(
            TemplateBinding(
                variable="allVersions[currentVersion].latestApiVersion",
                mode="static",
                static_value="2026-03-10",
            ),
            TemplateBinding(variable="apiVersion", mode="loop_variable"),
            TemplateBinding(
                variable="defaultRestApiVersion",
                mode="static",
                static_value="2022-11-28",
            ),
            TemplateBinding(
                variable="initialRestVersioningReleaseDate",
                mode="static",
                static_value="2026-03-10",
            ),
            TemplateBinding(
                variable="initialRestVersioningReleaseDateLong",
                mode="static",
                static_value="Tue, 10 Mar 2026",
            ),
            TemplateBinding(variable="secrets.GITHUB_TOKEN", mode="raw_literal_only"),
            TemplateBinding(
                variable='versionData.end_of_support | default: "Not yet scheduled"',
                mode="loop_derived",
            ),
        ),
    )


def test_renders_data_static_template_and_autotitle() -> None:
    renderer = ConstrainedAuthoredRenderer(
        _policy(),
        {"variables.product.github": "GitHub"},
    )
    source = (
        "{% data variables.product.github %} uses REST "
        "{{ defaultRestApiVersion }}. [AUTOTITLE](/rest/about)"
    )

    rendered, stats = renderer.render(source)

    assert rendered == "GitHub uses REST 2022-11-28. [/rest/about](/rest/about)"
    assert stats.data_substitution_count == 1
    assert stats.autotitle_replacement_count == 1


def test_renders_fpt_branch_and_skips_ghec_branch() -> None:
    renderer = ConstrainedAuthoredRenderer(_policy(), {})
    source = (
        "{% ifversion fpt %}FPT{% else %}OTHER{% endif %}|"
        "{% ifversion ghec %}GHEC{% else %}NOT-GHEC{% endif %}"
    )

    rendered, _ = renderer.render(source)

    assert rendered == "FPT|NOT-GHEC"


def test_renders_if_elsif_else_with_frozen_truth_table() -> None:
    renderer = ConstrainedAuthoredRenderer(_policy(), {})
    source = (
        '{% if query.apiVersion == nil or "2026-03-10" <= query.apiVersion %}'
        "CURRENT"
        "{% elsif ghes %}GHES{% else %}FALLBACK{% endif %}"
    )

    rendered, _ = renderer.render(source)

    assert rendered == "CURRENT"


def test_renders_api_version_loop_assignment_and_derived_value() -> None:
    renderer = ConstrainedAuthoredRenderer(_policy(), {})
    source = (
        "{% for apiVersion in allVersions[currentVersion].apiVersions %}"
        "{% assign versionData = tables.rest-api-versions.versions[apiVersion] %}"
        "{{ apiVersion }}={{ versionData.end_of_support | default: \"Not yet scheduled\" }};"
        "{% endfor %}"
    )

    rendered, stats = renderer.render(source)

    assert rendered == "2026-03-10=Not yet scheduled;2022-11-28=March 10, 2028;"
    assert stats.iteration_count == 2


def test_strips_variant_wrappers_and_replaces_exact_octicon() -> None:
    renderer = ConstrainedAuthoredRenderer(_policy(), {})
    source = (
        "{% cli %}CLI{% endcli %}"
        "{% curl %}CURL{% endcurl %}"
        "{% javascript %}JS{% endjavascript %}"
        '{% octicon "code" aria-hidden="true" aria-label="code" %}'
    )

    rendered, stats = renderer.render(source)

    assert rendered == "CLICURLJScode"
    assert stats.variant_block_count == 3
    assert stats.octicon_replacement_count == 1


def test_preserves_raw_secret_literal_without_evaluating_it() -> None:
    renderer = ConstrainedAuthoredRenderer(_policy(), {})
    source = "Before {% raw %}${{ secrets.GITHUB_TOKEN }}{% endraw %} after"

    rendered, stats = renderer.render(source)

    assert rendered == "Before ${{ secrets.GITHUB_TOKEN }} after"
    assert stats.preserved_raw_block_count == 1
    assert stats.preserved_raw_literal_template_count == 1
    assert count_active_unresolved_directives(rendered) == 0


def test_secret_template_outside_raw_fails_closed() -> None:
    renderer = ConstrainedAuthoredRenderer(_policy(), {})

    with pytest.raises(RenderContractError) as exc_info:
        renderer.render("{{ secrets.GITHUB_TOKEN }}")

    assert exc_info.value.code is RenderErrorCode.SECRET_RESOLUTION_FORBIDDEN


def test_unknown_construct_and_expression_fail_closed() -> None:
    renderer = ConstrainedAuthoredRenderer(_policy(), {})

    with pytest.raises(RenderContractError) as tag_error:
        renderer.render("{% include something %}")
    assert tag_error.value.code is RenderErrorCode.UNKNOWN_TAG

    with pytest.raises(RenderContractError) as expression_error:
        renderer.render("{% ifversion some-new-feature %}x{% endif %}")
    assert expression_error.value.code is RenderErrorCode.UNKNOWN_EXPRESSION


def test_liquid_trim_markers_apply_deterministically() -> None:
    renderer = ConstrainedAuthoredRenderer(_policy(), {})
    source = "A \n{%- ifversion fpt -%}\n B \n{%- endif %}\n C"

    rendered, _ = renderer.render(source)

    assert rendered == "AB\n C"


def test_inactive_branch_still_rejects_unfrozen_template() -> None:
    renderer = ConstrainedAuthoredRenderer(_policy(), {})
    source = "{% ifversion ghec %}{{ unexpected.value }}{% endif %}"

    with pytest.raises(RenderContractError) as exc_info:
        renderer.render(source)

    assert exc_info.value.code is RenderErrorCode.UNFROZEN_TEMPLATE


def test_active_unresolved_scan_allows_only_frozen_raw_secret_literal() -> None:
    assert count_active_unresolved_directives("${{ secrets.GITHUB_TOKEN }}") == 0
    assert count_active_unresolved_directives("{{ defaultRestApiVersion }}") == 1
    assert count_active_unresolved_directives("{% ifversion fpt %}") == 1
    assert count_active_unresolved_directives("[AUTOTITLE](/rest/example)") == 1


def test_data_reference_content_is_rendered_recursively() -> None:
    renderer = ConstrainedAuthoredRenderer(
        _policy(),
        {
            "reusables.rest-api.example": (
                "{% ifversion fpt %}GitHub {{ defaultRestApiVersion }}{% endif %}"
            )
        },
    )

    rendered, stats = renderer.render("{% data reusables.rest-api.example %}")

    assert rendered == "GitHub 2022-11-28"
    assert stats.data_substitution_count == 1


def test_data_reference_with_unreviewed_argument_fails_closed() -> None:
    renderer = ConstrainedAuthoredRenderer(
        _policy(),
        {"variables.product.github": "GitHub"},
    )

    with pytest.raises(RenderContractError) as exc_info:
        renderer.render("{% data variables.product.github unexpected %}")

    assert exc_info.value.code is RenderErrorCode.UNKNOWN_EXPRESSION
