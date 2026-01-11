from fastapi import HTTPException, status

class Medic1Exception(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class NotFoundException(Medic1Exception):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status_code.HTTP_404_NOT_FOUND, detail=detail)

class UnauthorizedException(Medic1Exception):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=status_code.HTTP_401_UNAUTHORIZED, detail=detail)

class ForbiddenException(Medic1Exception):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status_code.HTTP_403_FORBIDDEN, detail=detail)

class BadRequestException(Medic1Exception):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status_code.HTTP_400_BAD_REQUEST, detail=detail)
