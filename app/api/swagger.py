from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()

@router.get("/docs/swagger.json")
async def get_swagger_json() -> Dict[str, Any]:
    """Get Swagger JSON documentation"""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Pregnancy Agent API",
            "description": "AI-powered pregnancy companion agent API",
            "version": "0.1.0",
            "contact": {
                "name": "Pregnancy Agent Team",
                "email": "support@pregnancyagent.com"
            }
        },
        "servers": [
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            }
        ],
        "paths": {
            "/": {
                "get": {
                    "summary": "Health Check",
                    "description": "Check if the API is running",
                    "responses": {
                        "200": {
                            "description": "API is running",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "msg": {
                                                "type": "string",
                                                "example": "Pregnancy Agent API is running"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/chat": {
                "post": {
                    "summary": "Chat with Agent",
                    "description": "Send a message to the pregnancy agent and get a response",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "user_id": {
                                            "type": "string",
                                            "description": "User ID"
                                        },
                                        "message": {
                                            "type": "string",
                                            "description": "User message"
                                        },
                                        "context": {
                                            "type": "object",
                                            "description": "Additional context"
                                        }
                                    },
                                    "required": ["user_id", "message"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "response": {
                                                "type": "string",
                                                "description": "Agent response"
                                            },
                                            "actions": {
                                                "type": "array",
                                                "description": "Executed actions"
                                            },
                                            "context": {
                                                "type": "object",
                                                "description": "Conversation context"
                                            },
                                            "user_profile": {
                                                "type": "object",
                                                "description": "User profile"
                                            },
                                            "needs_profile": {
                                                "type": "boolean",
                                                "description": "Whether user needs to create profile"
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "/user-profile/{user_id}": {
                "get": {
                    "summary": "Get User Profile",
                    "description": "Get pregnancy profile for a user",
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            },
                            "description": "User ID"
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "User profile",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "user_id": {"type": "string"},
                                            "name": {"type": "string"},
                                            "age": {"type": "integer"},
                                            "pregnancy_week": {"type": "integer"},
                                            "lmp_date": {"type": "string", "format": "date"},
                                            "due_date": {"type": "string", "format": "date"},
                                            "emergency_contact": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "patch": {
                    "summary": "Update User Profile",
                    "description": "Update pregnancy profile for a user",
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            },
                            "description": "User ID"
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "age": {"type": "integer"},
                                        "lmp_date": {"type": "string", "format": "date"},
                                        "due_date": {"type": "string", "format": "date"},
                                        "emergency_contact": {"type": "string"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Updated user profile"
                        }
                    }
                }
            },
            "/medical/medical-documents": {
                "post": {
                    "summary": "Upload Medical Document",
                    "description": "Upload a medical document (PDF)",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "multipart/form-data": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "user_id": {"type": "string"},
                                        "doc_type": {"type": "string"},
                                        "document_date": {"type": "string", "format": "date"},
                                        "file": {
                                            "type": "string",
                                            "format": "binary"
                                        }
                                    },
                                    "required": ["user_id", "doc_type", "file"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Document uploaded successfully"
                        }
                    }
                }
            },
            "/tasks/{user_id}": {
                "get": {
                    "summary": "Get User Tasks",
                    "description": "Get tasks for a user",
                    "parameters": [
                        {
                            "name": "user_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            }
                        },
                        {
                            "name": "completed",
                            "in": "query",
                            "required": False,
                            "schema": {
                                "type": "boolean"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of tasks"
                        }
                    }
                }
            },
            "/tasks": {
                "post": {
                    "summary": "Create Task",
                    "description": "Create a new task",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "user_id": {"type": "string"},
                                        "title": {"type": "string"},
                                        "description": {"type": "string"},
                                        "task_type": {"type": "string"},
                                        "due_date": {"type": "string", "format": "date-time"},
                                        "priority": {"type": "integer"}
                                    },
                                    "required": ["user_id", "title", "description", "task_type"]
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Task created successfully"
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "UserProfile": {
                    "type": "object",
                    "properties": {
                        "user_id": {"type": "string"},
                        "name": {"type": "string"},
                        "age": {"type": "integer"},
                        "pregnancy_week": {"type": "integer"},
                        "lmp_date": {"type": "string", "format": "date"},
                        "due_date": {"type": "string", "format": "date"},
                        "emergency_contact": {"type": "string"}
                    }
                },
                "Task": {
                    "type": "object",
                    "properties": {
                        "task_id": {"type": "string"},
                        "user_id": {"type": "string"},
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "task_type": {"type": "string"},
                        "due_date": {"type": "string", "format": "date-time"},
                        "completed": {"type": "boolean"},
                        "priority": {"type": "integer"}
                    }
                },
                "MedicalDocument": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string"},
                        "user_id": {"type": "string"},
                        "doc_type": {"type": "string"},
                        "upload_date": {"type": "string", "format": "date-time"},
                        "status": {"type": "string"},
                        "chunks_count": {"type": "integer"}
                    }
                }
            }
        },
        "tags": [
            {
                "name": "Chat Agent",
                "description": "Chat with the pregnancy agent"
            },
            {
                "name": "User Profile",
                "description": "Manage user pregnancy profiles"
            },
            {
                "name": "Medical Documents",
                "description": "Upload and manage medical documents"
            },
            {
                "name": "Tasks",
                "description": "Manage pregnancy-related tasks"
            }
        ]
    }
