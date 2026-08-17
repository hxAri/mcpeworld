import enum
from typing import Any

from mcpeworld import Str


class WorldOperationResult( enum.Enum ):

    Success = "success"
    ErrorNullWorld = "error_null_world"
    ErrorEmptyOrNullData = "error_empty_or_null_data"
    ErrorNbtNull = "error_nbt_null"
    ErrorCorrupted = "error_corrupted"
    ErrorBusy = "error_busy"
    ErrorUndefined = "error_undefined"

    def withData( self, data:Any ) -> "OperationOutcome":
        return OperationOutcome( result=self, data=data )

    def withMessage( self, message:Str ) -> "OperationOutcome":
        return OperationOutcome( result=self, message=message )


class OperationOutcome:

    def __init__( self, result:WorldOperationResult, data:Any = None, message:Str = "" ):
        self.result:WorldOperationResult = result
        self.data:Any = data
        self.message:Str = message

    @property
    def isSuccess( self ) -> bool:
        return self.result == WorldOperationResult.Success

    def __repr__( self ) -> Str:
        return f"OperationOutcome(result={self.result}, message={self.message!r})"
