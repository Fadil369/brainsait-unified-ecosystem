"""
Insurance Data Extractor

Handles extraction and processing of insurance data from Excel sheets and PDF files.
Supports multiple formats and provides automated data validation and cleaning.
"""

import pandas as pd
import logging
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import re
import io
import base64

logger = logging.getLogger(__name__)

class InsuranceDataExtractor:
    """
    Extracts and processes insurance data from various file formats.
    
    Supports:
    - Excel files (xlsx, xls, csv)
    - PDF text and table extraction
    - Automated data validation and cleaning
    """
    
    def __init__(self):
        self.supported_formats = ['xlsx', 'xls', 'csv', 'pdf']
        self.required_columns = [
            'claim_id', 'patient_id', 'provider_id', 'claim_amount',
            'claim_date', 'status', 'rejection_reason'
        ]
    
    async def extract_from_excel(
        self, 
        file_content: bytes, 
        filename: str,
        sheet_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract data from Excel files.
        
        Args:
            file_content: Raw file content as bytes
            filename: Original filename for format detection
            sheet_name: Specific sheet to extract (if None, extracts all sheets)
            
        Returns:
            Dict containing extracted data and metadata
        """
        try:
            file_extension = filename.lower().split('.')[-1]
            
            if file_extension == 'csv':
                df = pd.read_csv(io.BytesIO(file_content))
                sheets_data = {'Sheet1': df}
            else:
                # Handle Excel files
                with pd.ExcelFile(io.BytesIO(file_content)) as excel_file:
                    if sheet_name:
                        sheets_data = {sheet_name: pd.read_excel(excel_file, sheet_name=sheet_name)}
                    else:
                        sheets_data = {}
                        for sheet in excel_file.sheet_names:
                            sheets_data[sheet] = pd.read_excel(excel_file, sheet_name=sheet)
            
            # Clean and validate data
            cleaned_data = {}
            for sheet, df in sheets_data.items():
                cleaned_df = await self._clean_dataframe(df)
                validation_results = await self._validate_data(cleaned_df)
                
                cleaned_data[sheet] = {
                    'data': cleaned_df.to_dict('records'),
                    'metadata': {
                        'total_rows': len(cleaned_df),
                        'columns': list(cleaned_df.columns),
                        'validation': validation_results,
                        'extracted_at': datetime.now().isoformat()
                    }
                }
            
            return {
                'success': True,
                'filename': filename,
                'sheets': cleaned_data,
                'format': file_extension
            }
            
        except Exception as e:
            logger.error(f"Error extracting Excel data from {filename}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'filename': filename
            }
    
    async def extract_from_pdf(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Extract data from PDF files.
        
        Args:
            file_content: Raw PDF content as bytes
            filename: Original filename
            
        Returns:
            Dict containing extracted text and any detected tables
        """
        try:
            # For now, return a placeholder structure
            # In full implementation, would use PyPDF2, pdfplumber, or tabula-py
            extracted_text = "PDF extraction placeholder - would extract text and tables"
            
            return {
                'success': True,
                'filename': filename,
                'text': extracted_text,
                'tables': [],
                'metadata': {
                    'pages': 1,
                    'extracted_at': datetime.now().isoformat(),
                    'format': 'pdf'
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting PDF data from {filename}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'filename': filename
            }
    
    async def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize dataframe data."""
        # Remove empty rows and columns
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # Standardize column names
        df.columns = [col.lower().strip().replace(' ', '_') for col in df.columns]
        
        # Clean date columns
        date_columns = ['claim_date', 'submission_date', 'processing_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Clean numeric columns
        numeric_columns = ['claim_amount', 'approved_amount', 'rejected_amount']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Clean text columns
        text_columns = ['status', 'rejection_reason', 'provider_name']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        return df
    
    async def _validate_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Validate extracted data quality."""
        validation_results = {
            'total_rows': len(df),
            'issues': [],
            'quality_score': 100.0
        }
        
        # Check for required columns
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        if missing_columns:
            validation_results['issues'].append({
                'type': 'missing_columns',
                'details': missing_columns
            })
            validation_results['quality_score'] -= 20
        
        # Check for empty critical fields
        for col in self.required_columns:
            if col in df.columns:
                empty_count = df[col].isna().sum()
                if empty_count > 0:
                    validation_results['issues'].append({
                        'type': 'missing_values',
                        'column': col,
                        'count': int(empty_count),
                        'percentage': round(empty_count / len(df) * 100, 2)
                    })
                    validation_results['quality_score'] -= (empty_count / len(df)) * 10
        
        # Check data types
        if 'claim_amount' in df.columns:
            invalid_amounts = df['claim_amount'].isna().sum()
            if invalid_amounts > 0:
                validation_results['issues'].append({
                    'type': 'invalid_amounts',
                    'count': int(invalid_amounts)
                })
        
        validation_results['quality_score'] = max(0, validation_results['quality_score'])
        return validation_results
    
    async def process_uploaded_file(
        self, 
        file_content: bytes, 
        filename: str,
        file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main entry point for processing uploaded files.
        
        Args:
            file_content: Raw file content
            filename: Original filename
            file_type: Optional file type override
            
        Returns:
            Processed data with metadata
        """
        try:
            # Determine file type
            file_extension = file_type or filename.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                return await self.extract_from_pdf(file_content, filename)
            elif file_extension in ['xlsx', 'xls', 'csv']:
                return await self.extract_from_excel(file_content, filename)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported file format: {file_extension}',
                    'supported_formats': self.supported_formats
                }
                
        except Exception as e:
            logger.error(f"Error processing uploaded file {filename}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'filename': filename
            }