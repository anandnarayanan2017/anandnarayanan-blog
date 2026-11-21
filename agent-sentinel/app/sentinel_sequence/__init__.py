"""Agent Sentinel — Phase 2: sequence modeling for agent behavior (prod)."""

from .config import SequenceConfig
from .detector import InsufficientDataError, SequenceDetector
from .drift import DriftReport, check_drift
from .evaluate import EvalReport, evaluate
from .markov import MarkovModel
from .registry import ModelBundle, ModelRegistry, RegistryError
from .scoring import SessionScore, StepSurprise, score_session
from .sessions import split_sessions
from .tokenizer import EOS, SOS, UNK, Tokenizer, event_to_token

__version__ = "0.2.0"

__all__ = [
    "EOS",
    "SOS",
    "UNK",
    "DriftReport",
    "EvalReport",
    "InsufficientDataError",
    "MarkovModel",
    "ModelBundle",
    "ModelRegistry",
    "RegistryError",
    "SequenceConfig",
    "SequenceDetector",
    "SessionScore",
    "StepSurprise",
    "Tokenizer",
    "check_drift",
    "evaluate",
    "event_to_token",
    "score_session",
    "split_sessions",
]
