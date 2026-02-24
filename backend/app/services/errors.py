class AppError(Exception):
    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int,
        details: object | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details


class NotFoundError(AppError):
    def __init__(self, message: str = "Entry not found") -> None:
        super().__init__(code="ENTRY_NOT_FOUND", message=message, status_code=404)


class EntryDateExistsError(AppError):
    def __init__(self, entry_date: str) -> None:
        super().__init__(
            code="ENTRY_DATE_EXISTS",
            message="An entry already exists for this date",
            status_code=409,
            details={"entry_date": entry_date},
        )
