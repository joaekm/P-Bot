import React from 'react';
import PropTypes from 'prop-types';
import { tokens } from '../tokens';
import { Check, Circle } from 'lucide-react';

/**
 * ProcessProgressBar Component
 * 
 * Vertical timeline showing the 4 process steps of the procurement flow.
 * Displays current step and marks completed steps with checkmarks.
 * 
 * Used in the sidebar for navigation and orientation.
 */
const ProcessProgressBar = ({ 
    steps = [], 
    currentStepIndex = 0,
    style = {}
}) => {
    return (
        <div 
            style={{
                display: 'flex',
                flexDirection: 'column',
                gap: tokens.spacing['2xl'],
                // padding, bg, shadow, radius removed - inherited from container
                fontFamily: tokens.typography.fontFamily,
                ...style
            }}
        >
            {/* Title removed as per requirements */}

            {steps.map((step, index) => {
                const isCompleted = index < currentStepIndex;
                const isCurrent = index === currentStepIndex;
                const isPending = index > currentStepIndex;

                return (
                    <div 
                        key={step.id || index}
                        style={{
                            display: 'flex',
                            alignItems: 'stretch', // Stretch to make line calculation easier? No, icon shouldn't stretch.
                            // Keep flex-start but ensure line covers full height
                            alignItems: 'flex-start',
                            gap: tokens.spacing.lg,
                            position: 'relative'
                        }}
                    >
                        {/* Connector Line */}
                        {index < steps.length - 1 && (
                            <div 
                                style={{
                                    position: 'absolute',
                                    left: '12px', // Center of 24px circle
                                    transform: 'translateX(-50%)', // Perfectly centered
                                    top: '24px', // Start exactly below circle
                                    width: '2px',
                                    height: `calc(100% + ${tokens.spacing['2xl']} - 24px)`, // Full height + gap - circle height
                                    // Logic: 100% is item height. Gap is spacing['2xl']. 
                                    // We start at 24px. So we lose 24px of the 100%.
                                    // So: (100% - 24px) + gap.
                                    backgroundColor: isCompleted 
                                        ? tokens.colors.status.success 
                                        : tokens.colors.neutral.border,
                                    zIndex: 0
                                }}
                            />
                        )}

                        {/* Step Icon */}
                        <div 
                            style={{
                                position: 'relative',
                                zIndex: 1,
                                width: '24px',
                                height: '24px',
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                backgroundColor: isCompleted 
                                    ? tokens.colors.status.success
                                    : isCurrent
                                    ? tokens.colors.brand.primary
                                    : tokens.colors.neutral.surface,
                                border: `2px solid ${
                                    isCompleted 
                                        ? tokens.colors.status.success
                                        : isCurrent
                                        ? tokens.colors.brand.primary
                                        : tokens.colors.neutral.border
                                }`,
                                boxSizing: 'border-box', // Ensure 24px is accurate
                                flexShrink: 0
                            }}
                        >
                            {isCompleted ? (
                                <Check size={14} color={tokens.colors.neutral.surface} strokeWidth={3} />
                            ) : isCurrent ? (
                                <Circle size={8} color={tokens.colors.neutral.surface} fill={tokens.colors.neutral.surface} />
                            ) : (
                                <div style={{
                                    width: '8px',
                                    height: '8px',
                                    borderRadius: '50%',
                                    backgroundColor: tokens.colors.neutral.border
                                }} />
                            )}
                        </div>

                        {/* Step Content */}
                        <div style={{ flex: 1, paddingTop: '2px' }}>
                            <div style={{
                                fontSize: tokens.typography.sizes.xs,
                                fontWeight: tokens.typography.weights.medium,
                                color: isCurrent 
                                    ? tokens.colors.brand.primary
                                    : isCompleted
                                    ? tokens.colors.status.successDark
                                    : tokens.colors.neutral.lightGrey,
                                marginBottom: '2px',
                                textTransform: 'uppercase',
                                letterSpacing: '0.5px'
                            }}>
                                Steg {index + 1}
                            </div>
                            <div style={{
                                fontSize: tokens.typography.sizes.sm,
                                fontWeight: isCurrent 
                                    ? tokens.typography.weights.semibold
                                    : tokens.typography.weights.regular,
                                color: isCurrent 
                                    ? tokens.colors.neutral.text
                                    : isCompleted
                                    ? tokens.colors.neutral.text
                                    : tokens.colors.neutral.lightGrey,
                                lineHeight: tokens.typography.lineHeights.normal
                            }}>
                                {step.title || step.section || `Steg ${index + 1}`}
                            </div>
                        </div>
                    </div>
                );
            })}
        </div>
    );
};

ProcessProgressBar.propTypes = {
    steps: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.string,
        title: PropTypes.string,
        section: PropTypes.string
    })).isRequired,
    currentStepIndex: PropTypes.number,
    style: PropTypes.object
};

export default ProcessProgressBar;

