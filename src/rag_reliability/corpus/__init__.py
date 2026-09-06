"""Corpus acquisition and catalog-building utilities."""

from rag_reliability.corpus.acquisition import acquire_file, acquire_selection, git_blob_sha1
from rag_reliability.corpus.catalog import build_operation_catalog, parse_candidate_operations
from rag_reliability.corpus.models import (
    AcquisitionReceipt,
    CorpusSourceSelectionPlan,
    Phase3aOperationCatalogCandidate,
    PinnedUpstreamFile,
)

__all__ = [
    "AcquisitionReceipt",
    "CorpusSourceSelectionPlan",
    "Phase3aOperationCatalogCandidate",
    "PinnedUpstreamFile",
    "acquire_file",
    "acquire_selection",
    "build_operation_catalog",
    "git_blob_sha1",
    "parse_candidate_operations",
]
