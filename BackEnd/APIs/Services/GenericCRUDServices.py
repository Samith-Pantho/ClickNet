from typing import Optional, Type, TypeVar, Generic, Any, Dict
from pydantic import BaseModel
from sqlalchemy import Table, insert, update, select
from sqlalchemy.exc import SQLAlchemyError
from Config.dbConnection import engine
from Schemas.shared import SystemLogErrorSchema
from .LogServices import AddLogOrError  # Import your engine

T = TypeVar('T', bound=BaseModel)
TableType = TypeVar('TableType', bound=Table)

class GenericInserter(Generic[T]):
    @staticmethod
    def insert_record(
        table,
        schema_model: Type[T],
        data: T,
        returning_fields=None
    ) -> Optional[T]:
        """
        Generic function to insert any record
        
        Args:
            table: SQLAlchemy Table object
            schema_model: Pydantic model class
            data: Pydantic model instance with data to insert
            returning_fields: List of columns to return after insert
            
        Returns:
            Inserted record as Pydantic model if successful
        """
        with engine.connect() as conn:
            try:
                # Convert Pydantic model to dict, exclude unset fields
                insert_data = data.model_dump(exclude_unset=True, by_alias=True)
                
                # Build the insert statement
                stmt = insert(table).values(**insert_data)
                
                if returning_fields:
                    stmt = stmt.returning(*returning_fields)
                
                # Execute and fetch results
                result = conn.execute(stmt)
                conn.commit()
                
                if returning_fields:
                    inserted = result.first()
                    return schema_model(**inserted._mapping) if inserted else None
                return None
                
            except SQLAlchemyError as ex:
                conn.rollback()
                AddLogOrError(SystemLogErrorSchema(
                    Msg = str(ex),
                    Type = "ERROR",
                    ModuleName = "GenericCRUDServices/insert_record",
                    CreatedBy = ""
                ))
                raise ValueError(f"Database insert failed: {str(ex)}")
            
class GenericUpdater(Generic[T, TableType]):
    @staticmethod
    def update_record(
        table: TableType,
        schema_model: Type[T],
        record_id: Any,
        update_data: T,
        id_column: str,
        exclude_fields: set = None
    ) -> Optional[T]:
        """
        Generic function to update any record in the database using engine connection
        
        Args:
            table: SQLAlchemy Table object
            schema_model: Pydantic model class
            record_id: ID of the record to update
            update_data: Pydantic model instance with update values
            id_column: Name of the primary key column (default: "id")
            exclude_fields: Set of field names to exclude from update
            
        Returns:
            Updated record as Pydantic model if successful, None otherwise
        """
        if exclude_fields is None:
            exclude_fields = set()
            
        with engine.connect() as _conn:
            try:
                # Start a transaction
                with _conn.begin():
                    # Convert Pydantic model to dict and remove unset/None values
                    update_dict = update_data.model_dump(
                        exclude_unset=True,
                        exclude_none=True,
                        exclude=exclude_fields,
                        by_alias=True
                    )
                    
                    # Remove the primary key if present in update data
                    update_dict.pop(id_column, None)
                    
                    if not update_dict:
                        raise ValueError("No valid fields provided for update")
                    
                    # Create and execute the update statement
                    stmt = (
                        update(table)
                        .where(getattr(table.c, id_column) == record_id)
                        .values(**update_dict)
                    )
                    
                    result = _conn.execute(stmt)
                    
                    if result.rowcount == 0:
                        raise ValueError(f"No record found with {id_column}: {record_id}")
                    
                    # Fetch and return the updated record
                    updated_record = _conn.execute(
                        select(table).where(getattr(table.c, id_column) == record_id)
                    ).mappings().fetchone()

                    if updated_record:
                        return schema_model(**updated_record)
                    return None
                    
            except SQLAlchemyError as ex:
                _conn.rollback()
                AddLogOrError(SystemLogErrorSchema(
                    Msg = str(ex),
                    Type = "ERROR",
                    ModuleName = "GenericCRUDServices/update_record",
                    CreatedBy = ""
                ))
                raise ValueError(f"Database error: {str(ex)}")
            except Exception as ex:
                _conn.rollback()
                AddLogOrError(SystemLogErrorSchema(
                    Msg = str(ex),
                    Type = "ERROR",
                    ModuleName = "GenericCRUDServices/update_record",
                    CreatedBy = ""
                ))
                raise ValueError(f"Error updating record: {str(ex)}")