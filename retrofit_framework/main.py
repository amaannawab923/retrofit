"""
FastAPI application entry point for the Warehouse Retrofit Framework.

This API provides endpoints for converting legacy warehouse layouts into
robotic-accommodated warehouses with navigation graphs, distance matrices,
charging stations, and traffic rules.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router

# Create FastAPI application
app = FastAPI(
    title="Warehouse Retrofit Framework API",
    description="""
    API for converting legacy warehouses to robotic-accommodated facilities.

    ## Features

    * **Navigation Graph Generation**: Creates a complete navigation graph with nodes and edges
    * **Distance Matrix Calculation**: Computes all-pairs shortest paths using Floyd-Warshall
    * **Charging Station Placement**: Strategic placement of charging stations
    * **Traffic Rules**: Defines one-way aisles, priority zones, and no-stopping zones
    * **Feasibility Assessment**: Scores the warehouse conversion feasibility (0-10 scale)

    ## Available Layouts

    * **Layout A**: Traditional 5-aisle warehouse (20m x 60m)

    ## Usage

    1. Call `/api/v1/convert/layouta` to convert Layout A
    2. Receive complete conversion data including navigation graph and recommendations
    3. Use the distance matrix for path planning
    4. Implement traffic rules for efficient robot operation
    """,
    version="1.0.0",
    contact={
        "name": "Warehouse Retrofit Framework",
        "url": "https://github.com/yourorg/warehouse-retrofit",
    },
    license_info={
        "name": "MIT",
    }
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes with prefix
app.include_router(router, prefix="/api/v1", tags=["conversion"])


@app.get(
    "/",
    summary="API Root",
    description="Get API information and documentation links"
)
async def root():
    """
    Root endpoint providing API information and navigation.

    Returns:
        dict: API metadata with links to documentation
    """
    return {
        "message": "Warehouse Retrofit Framework API",
        "version": "1.0.0",
        "description": "API for converting legacy warehouses to robotic-accommodated facilities",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "endpoints": {
            "convert_layout_a": "/api/v1/convert/layouta"
        }
    }


@app.get(
    "/health",
    summary="Health Check",
    description="Check API health status",
    tags=["health"]
)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "service": "warehouse-retrofit-api",
        "version": "1.0.0"
    }


# Application startup event
@app.on_event("startup")
async def startup_event():
    """
    Execute on application startup.

    Can be used to:
    - Initialize database connections
    - Load configuration
    - Warm up caches
    - Validate dependencies
    """
    print("=" * 60)
    print("Warehouse Retrofit Framework API - Starting Up")
    print("=" * 60)
    print(f"API Version: 1.0.0")
    print(f"Documentation: http://localhost:8000/docs")
    print(f"Health Check: http://localhost:8000/health")
    print("=" * 60)


# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Execute on application shutdown.

    Can be used to:
    - Close database connections
    - Clean up resources
    - Save state
    """
    print("=" * 60)
    print("Warehouse Retrofit Framework API - Shutting Down")
    print("=" * 60)


if __name__ == "__main__":
    import uvicorn

    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload during development
        log_level="info"
    )
