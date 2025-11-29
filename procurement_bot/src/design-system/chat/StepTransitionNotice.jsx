import React from 'react';
import PropTypes from 'prop-types';
import { tokens } from '../tokens';
import { CheckCircle, ArrowRight } from 'lucide-react';

/**
 * StepTransitionNotice Component
 * 
 * A specialized green notification that appears when transitioning
 * between process steps. Always uses success styling.
 * 
 * Shows: "✓ Steg X slutfört – går vidare till Steg Y"
 */
const StepTransitionNotice = ({ 
    fromStep = null,
    fromStepTitle = null,
    toStep = null,
    toStepTitle = null,
    message = null,
    style = {} 
}) => {
    // Build default message if not provided
    let displayMessage = message;
    if (!displayMessage) {
        if (fromStep && toStep) {
            displayMessage = `Steg ${fromStep}${fromStepTitle ? ` (${fromStepTitle})` : ''} slutfört`;
        } else if (toStep) {
            displayMessage = `Går vidare till Steg ${toStep}${toStepTitle ? `: ${toStepTitle}` : ''}`;
        } else {
            displayMessage = 'Steg slutfört';
        }
    }

    return (
        <div 
            style={{
                display: 'flex',
                alignItems: 'center',
                gap: tokens.spacing.md,
                padding: `${tokens.spacing.md} ${tokens.spacing.lg}`,
                backgroundColor: tokens.colors.status.successBg,
                borderRadius: tokens.borderRadius.pill,
                margin: `${tokens.spacing.xl} 0`,
                fontFamily: tokens.typography.fontFamily,
                justifyContent: 'center',
                ...style
            }}
        >
            <CheckCircle 
                size={18} 
                color={tokens.colors.status.success}
                style={{ flexShrink: 0 }}
            />
            <span 
                style={{
                    fontSize: tokens.typography.sizes.sm,
                    fontWeight: tokens.typography.weights.semibold,
                    color: tokens.colors.status.successDark
                }}
            >
                {displayMessage}
            </span>
            {toStep && toStepTitle && (
                <>
                    <ArrowRight 
                        size={16} 
                        color={tokens.colors.status.success}
                        style={{ flexShrink: 0 }}
                    />
                    <span 
                        style={{
                            fontSize: tokens.typography.sizes.sm,
                            fontWeight: tokens.typography.weights.semibold,
                            color: tokens.colors.status.successDark
                        }}
                    >
                        Steg {toStep}: {toStepTitle}
                    </span>
                </>
            )}
        </div>
    );
};

StepTransitionNotice.propTypes = {
    fromStep: PropTypes.number,
    fromStepTitle: PropTypes.string,
    toStep: PropTypes.number,
    toStepTitle: PropTypes.string,
    message: PropTypes.string,
    style: PropTypes.object
};

export default StepTransitionNotice;

