# FileCompareHub

FileCompareHub is a web application that provides an online platform for file comparison and script management. Users can upload, edit, and compare files with flexible regex-based matching, and manage Python scripts for automated comparisons.

## Features

1. **Online Editor**: Edit and view files with syntax highlighting for multiple languages
2. **File Comparison Tool**: Compare files using regex patterns with filtering and grouping options
3. **Script Registry**: Upload, manage, and run Python comparison scripts
4. **Comparison Constructor**: Visual builder for creating custom comparison workflows
5. **Template Management**: Save and reuse comparison configurations

## Supported File Types

- Excel files (.xlsx, .xls) - converted to text for comparison
- MIF files (.mif) - treated as structured text
- Text files (.txt) - line-by-line comparison
- Python scripts (.py) - for automated comparisons
- Other text-based configuration files

## Tech Stack

- **Backend**: Python with FastAPI
- **Frontend**: React.js with Material-UI
- **Database**: SQLite
- **Editor**: Monaco Editor
- **Deployment**: Docker & Docker Compose

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- Git (optional, for cloning the repository)

### Running with Docker Compose (Development)

1. Clone or download the repository:
   ```
   git clone <repository-url>
   cd filecomparehub
   ```

2. Build and start the services:
   ```
   docker-compose up --build
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Default login: admin / admin

### Running on a VPS (Production)

1. Clone or download the repository:
   ```
   git clone <repository-url>
   cd filecomparehub
   ```

2. Initialize data directory:
   ```
   # On Linux/Mac
   ./init.sh
   
   # On Windows
   .\init.ps1
   ```

3. Update the `.env` file with your production secrets:
   ```
   # Database configuration
   DB_PATH=/app/data/filecomparehub.db
   
   # Security secrets
   SECRET_KEY=your-super-secret-jwt-key-change-in-production
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   
   # Default admin user
   DEFAULT_ADMIN_USERNAME=admin
   DEFAULT_ADMIN_PASSWORD=your-secure-password
   
   # File upload settings
   MAX_FILE_SIZE=10485760  # 10MB in bytes
   
   # Frontend configuration
   REACT_APP_API_BASE_URL=http://your-domain.com
   ```

4. Build and start the services:
   ```
   docker-compose -f docker-compose.prod.yml up --build -d
   ```

5. Access the application:
   - Frontend: http://your-domain.com
   - Backend API: http://your-domain.com/api/
   - Default login: admin / your-secure-password

### Running Locally (Development)

#### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the backend server:
   ```
   python main.py
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

4. Access the application at http://localhost:3000

## API Endpoints

- `POST /auth/login` - User authentication
- `POST /upload` - File upload
- `POST /compare` - File comparison
- `GET /scripts` - List scripts
- `POST /scripts` - Create script
- `GET /scripts/{id}` - Get script
- `PUT /scripts/{id}` - Update script
- `DELETE /scripts/{id}` - Delete script
- `GET /comparisons` - List comparison templates
- `POST /comparisons` - Create comparison template
- `GET /comparisons/{id}` - Get comparison template
- `PUT /comparisons/{id}` - Update comparison template
- `DELETE /comparisons/{id}` - Delete comparison template

## Example Usage

1. **Upload and Compare Files**:
   - Navigate to the Editor to upload two files
   - Go to Comparison Constructor
   - Paste file contents into the inputs
   - Optionally add regex patterns for extraction
   - Run comparison and view results

2. **Create a Comparison Script**:
   - Go to Script Registry
   - Create a new Python script that implements your comparison logic
   - Save and run the script from the registry

3. **Save a Comparison Template**:
   - Configure a comparison in the Constructor
   - Go to Comparison Templates
   - Save the configuration as a reusable template

## Security

- JWT-based authentication
- File type validation
- Size limits for uploads (10MB default)
- Regex timeout protection to prevent ReDoS attacks

## Testing

The application includes unit tests for critical components:

- Backend API endpoints
- File processing functions
- Comparison logic

Run tests with:
```
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License.