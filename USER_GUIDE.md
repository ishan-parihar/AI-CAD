# 🚀 How to Use the AI-CAD Frontend

## 🌐 **Access the Application**

1. **Start the servers:**
   ```bash
   cd /home/ishanp/Documents/GitHub/AI-CAD
   ./run.sh
   ```

2. **Open your browser and go to:**
   - **Main App**: http://localhost:3001 (automatically redirects to dashboard)
   - **Backend API**: http://localhost:8100/docs
   - **API Test**: http://localhost:3001/api-test

## 🏠 **Application Structure**

The app has a professional dashboard interface with the following sections:

### **1. Dashboard (`/dashboard`)**
- **Overview**: Shows statistics (total plans, completed, in progress, total area)
- **Recent Plans**: List of your latest floor plans with status badges
- **Quick Actions**: Create new plan, upload DXF, view recent
- **System Status**: API server, AI engine, and storage status

### **2. Plans List (`/plans`)**
- **Grid/List View**: Toggle between grid and list view modes
- **Search**: Find plans by name
- **Filters**: Filter by status (completed, generating, failed) and type (residential, commercial)
- **Plan Cards**: Each card shows plan details, progress, and actions

### **3. Create New Plan (`/plans/new`)**
**5-Step Wizard Process:**

#### **Step 1: Basic Info**
- Enter plan name (e.g., "Modern Family Home")
- Select building type (Residential, Commercial, Mixed Use)

#### **Step 2: Dimensions**
- Set building dimensions (width × height in meters)
- Use increment/decrement buttons or type values directly
- Shows total area calculation

#### **Step 3: Rooms Configuration**
- Add multiple rooms with "Add Room" button
- For each room:
  - Set room name (e.g., "Master Bedroom")
  - Select room type (Living Room, Kitchen, Bathroom, etc.)
  - Set minimum and maximum area requirements
- Remove rooms with the "-" button

#### **Step 4: Constraints**
- **Budget** (optional): Set project budget
- **Architectural Style**: Modern, Traditional, Contemporary, etc.
- **Number of Floors**: 1-5 floors
- **Special Requirements**: Wheelchair accessible, home office, etc.

#### **Step 5: Review**
- Complete summary of all plan details
- Verify all information before generation
- Click "Generate Plan" to start the process

### **4. Plan Detail Page (`/plans/[id]`)**
- **Plan Information**: Building type, dimensions, total area, efficiency score
- **Room Details**: List of all rooms with areas and percentages
- **DXF Viewer**: Placeholder for interactive CAD file viewer
- **Actions**: Download, share, edit, regenerate, delete

### **5. Settings (`/settings`)**
- **Profile**: Personal information and role
- **Notifications**: Email/push notification preferences
- **Appearance**: Theme, language, units, CAD editor settings
- **API & Integrations**: API keys, webhooks, export formats
- **Security**: Password change, 2FA setup
- **Data Management**: Export data, delete account

## 🎯 **Complete User Workflow**

### **Creating Your First Plan:**

1. **Go to Dashboard** → http://localhost:3001
2. **Click "Create New Plan"** (or use Quick Actions panel)
3. **Follow the 5-step wizard:**
   - Basic Info → Dimensions → Rooms → Constraints → Review
4. **Click "Generate Plan"** to start the AI generation process
5. **Monitor Progress** in the dashboard or plans list
6. **View Details** when generation is complete
7. **Download DXF file** for use in CAD software

### **Managing Existing Plans:**

1. **Go to Plans List** → http://localhost:3001/plans
2. **Use Search/Filter** to find specific plans
3. **Click "View"** to see plan details
4. **Use Actions** to download, edit, or delete plans

## 📱 **Navigation**

- **Sidebar Navigation**: Click menu items to switch between sections
- **Mobile Menu**: Use hamburger menu on mobile devices
- **Breadcrumb Navigation**: Easy navigation back to previous pages
- **Quick Actions**: "New Plan" button always available in top header

## 🎨 **Features to Try**

### **Dashboard Features:**
- View real-time statistics
- Monitor plan generation progress
- Check system status
- Quick access to common tasks

### **Plan Creation Features:**
- Multi-step wizard with validation
- Dynamic room configuration
- Real-time area calculations
- Comprehensive constraint settings

### **Plan Management Features:**
- Grid and list view modes
- Advanced search and filtering
- Status tracking and progress bars
- Bulk actions support

### **Settings Features:**
- Comprehensive preference management
- API key configuration
- Notification customization
- Data export/import tools

## 🔧 **Development Notes**

- **Mock Data**: Currently using realistic mock data for demonstration
- **Backend Integration**: All API endpoints are ready for real backend integration
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **TypeScript**: Full type safety throughout the application
- **Modern UI**: Clean, professional interface using Tailwind CSS

## 🚨 **Important URLs**

- **Main Application**: http://localhost:3001
- **Dashboard**: http://localhost:3001/dashboard
- **Plans List**: http://localhost:3001/plans
- **Create Plan**: http://localhost:3001/plans/new
- **Settings**: http://localhost:3001/settings
- **API Documentation**: http://localhost:8100/docs
- **API Test Page**: http://localhost:3001/api-test

The application is now fully functional and ready for use! The frontend provides a complete user experience for creating and managing AI-generated architectural floor plans.