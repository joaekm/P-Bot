/**
 * Component Registry for Server-Driven UI
 * 
 * Maps widget_type strings from backend to React components.
 * When the backend returns a stream_widget, we look up the component here.
 */

// Import widget components
import DebugCard from '../design-system/components/DebugCard';
import ResourceSummaryCard from '../design-system/components/ResourceSummaryCard';

/**
 * Registry of all available stream widgets.
 * 
 * The key is the widget_type string from the backend.
 * The value is the React component to render.
 */
export const WIDGET_REGISTRY = {
  // Debug/test widget
  'DebugCard': DebugCard,
  
  // Resource-related widgets
  'ResourceSummaryCard': ResourceSummaryCard,
  
  // Level selection widget (placeholder)
  'LevelSelector': null, // TODO: Implement
  
  // Cost estimate widget (placeholder)
  'CostEstimate': null, // TODO: Implement
  
  // Strategy summary widget (placeholder)
  'StrategySummary': null, // TODO: Implement
};

/**
 * Get a component from the registry.
 * 
 * @param {string} widgetType - The widget type from backend
 * @returns {React.Component|null} - The component or null if not found
 */
export function getWidgetComponent(widgetType) {
  const component = WIDGET_REGISTRY[widgetType];
  
  if (!component) {
    console.warn(`Widget type "${widgetType}" not found in registry`);
    return null;
  }
  
  return component;
}

/**
 * Check if a widget type is registered.
 * 
 * @param {string} widgetType - The widget type to check
 * @returns {boolean}
 */
export function isWidgetRegistered(widgetType) {
  return widgetType in WIDGET_REGISTRY && WIDGET_REGISTRY[widgetType] !== null;
}

export default WIDGET_REGISTRY;




