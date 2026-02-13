# Component Patterns

## Card Components

### Basic Card Pattern

```typescript
// Tailwind implementation
const Card = ({ title, description, image }) => (
  <div className="bg-white rounded-lg shadow-md overflow-hidden">
    {image && (
      <img src={image} alt={title} className="w-full h-48 object-cover" />
    )}
    <div className="p-6">
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      <p className="text-gray-600">{description}</p>
    </div>
  </div>
);

// CSS Modules implementation
const Card = ({ title, description, image }) => (
  <div className={styles.card}>
    {image && (
      <img src={image} alt={title} className={styles.cardImage} />
    )}
    <div className={styles.cardContent}>
      <h3 className={styles.cardTitle}>{title}</h3>
      <p className={styles.cardDescription}>{description}</p>
    </div>
  </div>
);
```

### Card with Actions

```typescript
const ActionCard = ({ title, actions }) => (
  <div className="bg-white rounded-lg shadow-md p-6">
    <div className="flex justify-between items-start">
      <h3 className="text-xl font-semibold">{title}</h3>
      <div className="flex gap-2">
        {actions.map((action, index) => (
          <button
            key={index}
            onClick={action.onClick}
            className="p-2 hover:bg-gray-100 rounded-md transition-colors"
          >
            {action.icon}
          </button>
        ))}
      </div>
    </div>
  </div>
);
```

## Navigation Patterns

### Top Navigation Bar

```typescript
const NavBar = ({ logo, links, actions }) => (
  <nav className="bg-white border-b border-gray-200">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center h-16">
        {/* Logo */}
        <div className="flex-shrink-0">
          {logo}
        </div>
        
        {/* Links */}
        <div className="hidden md:flex space-x-8">
          {links.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-gray-700 hover:text-gray-900 px-3 py-2 text-sm font-medium"
            >
              {link.label}
            </a>
          ))}
        </div>
        
        {/* Actions */}
        <div className="flex items-center space-x-4">
          {actions}
        </div>
      </div>
    </div>
  </nav>
);
```

### Sidebar Navigation

```typescript
const Sidebar = ({ items, collapsed = false }) => (
  <aside className={`
    ${collapsed ? 'w-16' : 'w-64'}
    bg-gray-900 h-screen transition-all duration-300
  `}>
    <nav className="mt-8">
      {items.map((item) => (
        <a
          key={item.id}
          href={item.href}
          className="flex items-center px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
        >
          <span className="mr-3">{item.icon}</span>
          {!collapsed && <span>{item.label}</span>}
        </a>
      ))}
    </nav>
  </aside>
);
```

## Form Components

### Input Field Pattern

```typescript
const InputField = ({ 
  label, 
  type = "text", 
  placeholder, 
  value, 
  onChange, 
  error 
}) => (
  <div className="mb-4">
    {label && (
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
    )}
    <input
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className={`
        w-full px-3 py-2 border rounded-md
        focus:outline-none focus:ring-2 focus:ring-blue-500
        ${error ? 'border-red-500' : 'border-gray-300'}
      `}
    />
    {error && (
      <p className="mt-1 text-sm text-red-600">{error}</p>
    )}
  </div>
);
```

### Select Dropdown

```typescript
const Select = ({ label, options, value, onChange }) => (
  <div className="mb-4">
    {label && (
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
    )}
    <select
      value={value}
      onChange={onChange}
      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
    >
      <option value="">Select an option</option>
      {options.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label}
        </option>
      ))}
    </select>
  </div>
);
```

### Checkbox Group

```typescript
const CheckboxGroup = ({ label, options, selected, onChange }) => (
  <div className="mb-4">
    {label && (
      <label className="block text-sm font-medium text-gray-700 mb-2">
        {label}
      </label>
    )}
    <div className="space-y-2">
      {options.map((option) => (
        <label key={option.value} className="flex items-center">
          <input
            type="checkbox"
            value={option.value}
            checked={selected.includes(option.value)}
            onChange={(e) => onChange(option.value, e.target.checked)}
            className="mr-2 h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
          />
          <span className="text-sm text-gray-700">{option.label}</span>
        </label>
      ))}
    </div>
  </div>
);
```

## Modal Implementations

### Basic Modal

```typescript
const Modal = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) return null;
  
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full">
          {/* Header */}
          <div className="px-6 py-4 border-b">
            <h3 className="text-lg font-semibold">{title}</h3>
            <button
              onClick={onClose}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>
          
          {/* Content */}
          <div className="px-6 py-4">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
};
```

### Dialog with Actions

```typescript
const Dialog = ({ 
  isOpen, 
  onClose, 
  title, 
  message, 
  onConfirm, 
  confirmText = "Confirm",
  cancelText = "Cancel" 
}) => (
  <Modal isOpen={isOpen} onClose={onClose} title={title}>
    <p className="text-gray-600 mb-6">{message}</p>
    <div className="flex justify-end gap-3">
      <button
        onClick={onClose}
        className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
      >
        {cancelText}
      </button>
      <button
        onClick={onConfirm}
        className="px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700"
      >
        {confirmText}
      </button>
    </div>
  </Modal>
);
```

## Grid Systems

### Responsive Grid

```typescript
const Grid = ({ columns = { sm: 1, md: 2, lg: 3, xl: 4 }, children }) => (
  <div className={`
    grid gap-6
    grid-cols-${columns.sm}
    md:grid-cols-${columns.md}
    lg:grid-cols-${columns.lg}
    xl:grid-cols-${columns.xl}
  `}>
    {children}
  </div>
);
```

### Masonry Grid

```typescript
const MasonryGrid = ({ children, columns = 3 }) => {
  const columnWrapper = {};
  const result = [];
  
  // Distribute children into columns
  for (let i = 0; i < columns; i++) {
    columnWrapper[`column${i}`] = [];
  }
  
  React.Children.forEach(children, (child, index) => {
    const columnIndex = index % columns;
    columnWrapper[`column${columnIndex}`].push(child);
  });
  
  // Create column elements
  for (let i = 0; i < columns; i++) {
    result.push(
      <div key={i} className="flex flex-col gap-4">
        {columnWrapper[`column${i}`]}
      </div>
    );
  }
  
  return (
    <div className="flex gap-4">
      {result}
    </div>
  );
};
```

## Button Patterns

### Button Variants

```typescript
const Button = ({ 
  variant = 'primary', 
  size = 'md', 
  children, 
  onClick,
  disabled = false 
}) => {
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700',
    secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
    outline: 'border-2 border-gray-300 text-gray-700 hover:bg-gray-50',
    ghost: 'text-gray-700 hover:bg-gray-100',
    danger: 'bg-red-600 text-white hover:bg-red-700'
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  };
  
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`
        ${variants[variant]}
        ${sizes[size]}
        rounded-md font-medium transition-colors
        disabled:opacity-50 disabled:cursor-not-allowed
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
      `}
    >
      {children}
    </button>
  );
};
```

### Icon Button

```typescript
const IconButton = ({ icon, label, onClick, size = 'md' }) => {
  const sizes = {
    sm: 'p-1',
    md: 'p-2',
    lg: 'p-3'
  };
  
  return (
    <button
      onClick={onClick}
      aria-label={label}
      className={`
        ${sizes[size]}
        rounded-md text-gray-700 hover:bg-gray-100
        focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500
      `}
    >
      {icon}
    </button>
  );
};
```

## Loading States

### Skeleton Loader

```typescript
const Skeleton = ({ width, height, className = '' }) => (
  <div
    className={`animate-pulse bg-gray-200 rounded ${className}`}
    style={{ width, height }}
  />
);

const CardSkeleton = () => (
  <div className="bg-white rounded-lg shadow-md p-6">
    <Skeleton height={24} className="mb-4" />
    <Skeleton height={16} className="mb-2" />
    <Skeleton height={16} width="80%" />
  </div>
);
```

### Spinner

```typescript
const Spinner = ({ size = 'md' }) => {
  const sizes = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };
  
  return (
    <div className={`${sizes[size]} animate-spin`}>
      <svg
        className="text-gray-300"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
        />
      </svg>
    </div>
  );
};
```
