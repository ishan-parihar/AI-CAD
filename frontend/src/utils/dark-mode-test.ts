// Simple test to verify dark mode styling fixes
// This file can be used to manually test the dark mode functionality

export const testDarkMode = () => {
  console.log('🎨 Testing Dark Mode Styling Fixes');
  
  // Test 1: Check if CSS variables are properly set
  const rootStyles = getComputedStyle(document.documentElement);
  const primaryColor = rootStyles.getPropertyValue('--primary');
  const foregroundColor = rootStyles.getPropertyValue('--foreground');
  
  console.log('✅ CSS Variables:', { primaryColor, foregroundColor });
  
  // Test 2: Check if dark mode class can be applied
  const htmlElement = document.documentElement;
  const hasDarkClass = htmlElement.classList.contains('dark');
  console.log('✅ Dark mode class present:', hasDarkClass);
  
  // Test 3: Check if plans/new page highlighting elements exist
  const highlightedOptions = document.querySelectorAll('[class*="border-primary"][class*="bg-primary"]');
  console.log('✅ Highlighted options found:', highlightedOptions.length);
  
  // Test 4: Check if semantic color classes are being used
  const semanticElements = document.querySelectorAll('[class*="text-foreground"], [class*="text-muted-foreground"], [class*="bg-card"], [class*="border-input"]');
  console.log('✅ Semantic color elements found:', semanticElements.length);
  
  console.log('🎉 Dark mode styling test completed!');
};

// Export for manual testing in browser console
if (typeof window !== 'undefined') {
  (window as any).testDarkMode = testDarkMode;
}