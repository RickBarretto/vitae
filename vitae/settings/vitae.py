"""Environment Settings."""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sqlalchemy import create_engine
import tomllib

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine

__all__ = ["Vitae"]


@dataclass(frozen=True, kw_only=True)
class PostgresUser:
    """Postgres' Database User Settings."""

    name: str = "postgres"
    password: str

    def __post_init__(self) -> None:
        if not all((self.name, self.password)):
            message: str = f"Missing fields {self}"
            raise ValueError(message)

    def __str__(self) -> str:
        return f"{self.name}:{self.password}"


@dataclass(frozen=True, kw_only=True)
class PostgresDatabase:
    """Postgres' Database Settings."""

    name: str
    host: str = "127.0.0.1"
    port: int = 5433

    flush_every: int = 100

    def __post_init__(self) -> None:
        if not all((self.name, self.host, self.port)):
            message: str = f"Missing fields {self}"
            raise ValueError(message)

    def __str__(self) -> str:
        return f"{self.host}:{self.port}/{self.name}"


@dataclass(frozen=True, kw_only=True)
class PostgresSettings:
    """Postgres' Settings."""

    user: PostgresUser
    db: PostgresDatabase

    @property
    def url(self) -> str:
        """Postgres URL from vitae.toml file."""
        return f"postgresql+psycopg://{self.user}@{self.db}"

    @cached_property
    def engine(self) -> Engine:
        """SQLAlchemy Engine."""
        return create_engine(self.url)

    @cached_property
    def verbose_engine(self) -> Engine:
        """SQLAlchemy Engine.

        The engine is verbose, so every event will be logged on terminal.
        """
        return create_engine(self.url, echo=True)


@dataclass(frozen=True, kw_only=True)
class PathsSettings:
    """Paths' Settings for Vitae.

    Note:
    ----
    `_curricula` must exist and be a directory.

    """

    logs: Path = Path("logs/")
    _curricula: Path = Path("all_files")

    def __post_init__(self) -> None:
        if not self._curricula.exists():
            message: str = "Curricula must exist"
            raise ValueError(message)

        if not self._curricula.is_dir():
            message: str = "Curricula must be a directory"
            raise ValueError(message)

    @property
    def curricula(self) -> Path:
        """Absolute curricula's directory.

        Note:
        ----
        This property exists to ensure curricula's path is always absolute.

        """
        return self._curricula.absolute()


@dataclass(frozen=True, kw_only=True)
class Vitae:
    """Settings loaded from `vitae.toml`."""

    postgres: PostgresSettings
    paths: PathsSettings
    in_production: bool = False

    @staticmethod
    def from_toml(file: Path | str = Path("vitae.toml")) -> Vitae:
        """Load data from TOML file.

        Parameters
        ----------
        file: Path | str
            This parameter is smarth enough to know when this is a file path,
            or a content of one.

            If you pass a string that ends with `.toml` this will be transformed
            into a Path.

        Returns
        -------
        Parsed data.

        """
        if isinstance(file, str) and not file.endswith(".toml"):
            return _vitae_from_parsed(tomllib.loads(file))

        with Path(file).open("rb") as f:
            return _vitae_from_parsed(tomllib.load(f))

    def with_logs(self, directory: Path = Path("logs")) -> Vitae:
        """Change the current log directory.

        Returns
        -------
        New modified instance of itself.

        """
        return replace(self, paths=replace(self.paths, logs=directory))

    @property
    def in_development(self) -> bool:  # noqa: D102
        return not self.in_production


def _vitae_from_parsed(data: dict[str, Any]) -> Vitae:
    """Parse data from dictionary.

    Use the functions `_from_file` or `_from_toml` to get `data`.
    """  # noqa: DOC201
    in_production: bool = data["project"].get("in_production", False)
    postgres: dict = data.get("postgres") or {}

    paths: dict = data.get("paths") or {}

    pg_db = PostgresDatabase(
        name=postgres["database"]["name"],
        host=postgres["database"].get("host", "127.0.0.1"),
        port=postgres["database"].get("port", 5433),
        flush_every=postgres["database"].get("flush_every", 100),
    )

    pg_user = PostgresUser(
        name=postgres["user"]["name"],
        password=postgres["user"]["password"],
    )

    return Vitae(
        in_production=in_production,
        postgres=PostgresSettings(user=pg_user, db=pg_db),
        paths=PathsSettings(
            _curricula=Path(paths.get("curricula") or "all_files"),
        ),
    )
