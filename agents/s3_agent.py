import asyncio
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import List, Dict, Any
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from models import AgentResponse, AgentType
from config import settings
import logging

logger = logging.getLogger(__name__)

class S3Agent(BaseAgent):
    """Agent for searching and accessing AWS S3 buckets"""
    
    def __init__(self):
        super().__init__(AgentType.S3)
        self.s3_client = None
        self.s3_resource = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize S3 client and resource"""
        try:
            if settings.aws_access_key_id and settings.aws_secret_access_key:
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    region_name=settings.aws_region
                )
                self.s3_resource = boto3.resource(
                    's3',
                    aws_access_key_id=settings.aws_access_key_id,
                    aws_secret_access_key=settings.aws_secret_access_key,
                    region_name=settings.aws_region
                )
                self.logger.info("S3 client initialized successfully")
            else:
                self.logger.warning("AWS credentials not configured")
        except Exception as e:
            self.logger.error(f"Failed to initialize S3 client: {str(e)}")
    
    async def is_relevant(self, query: str) -> bool:
        """Check if query is relevant to S3 operations"""
        s3_keywords = [
            's3', 'bucket', 'aws', 'amazon', 'object', 'file', 'storage',
            'cloud', 'upload', 'download', 'key', 'prefix', 'folder'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in s3_keywords)
    
    async def search(self, query: str, max_results: int = 10) -> AgentResponse:
        """Search S3 objects based on query"""
        if not self.s3_client:
            return self.create_response(
                success=False,
                data=[],
                error="S3 client not initialized. Please check AWS configuration."
            )
        
        try:
            search_terms = self._extract_search_terms(query)
            bucket_name = self._extract_bucket_name(query) or settings.s3_bucket_name
            
            if not bucket_name:
                return self.create_response(
                    success=False,
                    data=[],
                    error="No S3 bucket specified in query or configuration"
                )
            
            # Search objects in the bucket
            objects = await self._search_objects(bucket_name, search_terms, max_results)
            
            return self.create_response(
                success=True,
                data=objects,
                metadata={
                    'bucket': bucket_name,
                    'search_terms': search_terms,
                    'total_found': len(objects)
                }
            )
            
        except Exception as e:
            self.logger.error(f"S3 search failed: {str(e)}")
            return self.create_response(
                success=False,
                data=[],
                error=f"S3 search failed: {str(e)}"
            )
    
    async def _search_objects(self, bucket_name: str, search_terms: List[str], max_results: int) -> List[Dict[str, Any]]:
        """Search for objects in S3 bucket"""
        objects = []
        
        try:
            # List objects with pagination
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket=bucket_name)
            
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        # Check if object key matches search terms
                        if self._matches_search_terms(obj['Key'], search_terms):
                            object_info = {
                                'key': obj['Key'],
                                'size': obj['Size'],
                                'last_modified': obj['LastModified'].isoformat(),
                                'storage_class': obj.get('StorageClass', 'STANDARD'),
                                'etag': obj['ETag'].strip('"'),
                                'bucket': bucket_name,
                                'url': f"s3://{bucket_name}/{obj['Key']}"
                            }
                            
                            # Try to get content type
                            try:
                                head_response = await asyncio.get_event_loop().run_in_executor(
                                    None,
                                    lambda: self.s3_client.head_object(Bucket=bucket_name, Key=obj['Key'])
                                )
                                object_info['content_type'] = head_response.get('ContentType', 'unknown')
                                object_info['metadata'] = head_response.get('Metadata', {})
                            except Exception:
                                object_info['content_type'] = 'unknown'
                            
                            objects.append(object_info)
                            
                            if len(objects) >= max_results:
                                return objects
                
        except ClientError as e:
            self.logger.error(f"Error listing S3 objects: {str(e)}")
            raise
        
        return objects
    
    async def get_object_content(self, bucket_name: str, object_key: str, max_size: int = 1024 * 1024) -> Dict[str, Any]:
        """Get content of an S3 object (limited size for text files)"""
        try:
            # Check object size first
            head_response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.head_object(Bucket=bucket_name, Key=object_key)
            )
            
            object_size = head_response['ContentLength']
            if object_size > max_size:
                return {
                    'error': f'Object too large ({object_size} bytes). Maximum size: {max_size} bytes',
                    'success': False
                }
            
            # Get object content
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.get_object(Bucket=bucket_name, Key=object_key)
            )
            
            content = response['Body'].read()
            
            # Try to decode as text
            try:
                text_content = content.decode('utf-8')
                return {
                    'key': object_key,
                    'bucket': bucket_name,
                    'content': text_content,
                    'content_type': response.get('ContentType', 'unknown'),
                    'size': len(content),
                    'last_modified': response.get('LastModified', '').isoformat() if response.get('LastModified') else '',
                    'success': True
                }
            except UnicodeDecodeError:
                return {
                    'key': object_key,
                    'bucket': bucket_name,
                    'content': f'Binary content ({len(content)} bytes)',
                    'content_type': response.get('ContentType', 'unknown'),
                    'size': len(content),
                    'last_modified': response.get('LastModified', '').isoformat() if response.get('LastModified') else '',
                    'success': True
                }
                
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    async def list_buckets(self) -> Dict[str, Any]:
        """List all accessible S3 buckets"""
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.list_buckets()
            )
            
            buckets = []
            for bucket in response['Buckets']:
                buckets.append({
                    'name': bucket['Name'],
                    'creation_date': bucket['CreationDate'].isoformat()
                })
            
            return {
                'buckets': buckets,
                'success': True
            }
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    async def get_bucket_info(self, bucket_name: str) -> Dict[str, Any]:
        """Get information about a specific bucket"""
        try:
            # Get bucket location
            location = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.get_bucket_location(Bucket=bucket_name)
            )
            
            # Count objects (limited to first 1000 for performance)
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1000)
            )
            
            object_count = response.get('KeyCount', 0)
            total_size = sum(obj['Size'] for obj in response.get('Contents', []))
            
            return {
                'name': bucket_name,
                'region': location.get('LocationConstraint', 'us-east-1'),
                'object_count': object_count,
                'total_size': total_size,
                'success': True
            }
            
        except Exception as e:
            return {'error': str(e), 'success': False}
    
    def _extract_search_terms(self, query: str) -> List[str]:
        """Extract search terms from query"""
        stop_words = {'find', 'search', 'show', 'get', 's3', 'bucket', 'object', 'file', 'in', 'the', 'a', 'an'}
        words = query.lower().split()
        search_terms = [word for word in words if word not in stop_words and len(word) > 2]
        return search_terms
    
    def _extract_bucket_name(self, query: str) -> str:
        """Extract bucket name from query"""
        words = query.split()
        for i, word in enumerate(words):
            if word.lower() in ['bucket', 'in'] and i + 1 < len(words):
                return words[i + 1]
        return None
    
    def _matches_search_terms(self, key: str, search_terms: List[str]) -> bool:
        """Check if S3 object key matches search terms"""
        if not search_terms:
            return True
        
        key_lower = key.lower()
        return any(term.lower() in key_lower for term in search_terms)
    
    async def health_check(self) -> bool:
        """Check S3 connection health"""
        if not self.s3_client:
            return False
        
        try:
            # Try to list buckets
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.s3_client.list_buckets()
            )
            return True
        except Exception as e:
            self.logger.error(f"S3 health check failed: {str(e)}")
            return False
