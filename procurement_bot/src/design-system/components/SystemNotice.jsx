import React from 'react';
import PropTypes from 'prop-types';
import { tokens } from '../tokens';
import { Info, CheckCircle, AlertTriangle } from 'lucide-react';

/**
 * SystemNotice Component
 * 
 * Displays system notifications within the chat flow.
 * Three types: info (blue), success (green), warning (red/orange)
 * 
 * Used for:
 * - Pedagogical tips (info)
 * - Checkpoints and confirmations (success)
 * - Rule warnings and constraints (warning)
 */
const SystemNotice = ({ 
    type = 'info', 
    children, 
    title = null,
    icon: CustomIcon = null,
    style = {} 
}) => {
    // Color mappings for different notice types
    const typeStyles = {
        info: {
            background: tokens.colors.status.infoBg,
            border: tokens.colors.status.info,
            text: tokens.colors.status.infoDark,
            icon: Info
        },
        success: {
            background: tokens.colors.status.successBg,
            border: tokens.colors.status.success,
            text: tokens.colors.status.successDark,
            icon: CheckCircle
        },
        warning: {
            background: tokens.colors.status.warningBg,
            border: tokens.colors.status.warning,
            text: tokens.colors.status.warningDark,
            icon: AlertTriangle
        }
    };

    const currentStyle = typeStyles[type] || typeStyles.info;
    const IconComponent = CustomIcon || currentStyle.icon;

    return (
        <div 
            style={{
                display: 'flex',
                gap: tokens.spacing.md,
                padding: tokens.spacing.lg,
                backgroundColor: currentStyle.background,
                borderLeft: `4px solid ${currentStyle.border}`,
                borderRadius: tokens.borderRadius.sm,
                margin: `${tokens.spacing.lg} 0`,
                fontFamily: tokens.typography.fontFamily,
                ...style
            }}
        >
            <div style={{ 
                flexShrink: 0,
                marginTop: '2px'
            }}>
                <IconComponent 
                    size={20} 
                    color={currentStyle.border}
                />
            </div>
            <div style={{ flex: 1 }}>
                {title && (
                    <div style={{
                        fontWeight: tokens.typography.weights.semibold,
                        fontSize: tokens.typography.sizes.md,
                        color: currentStyle.text,
                        marginBottom: tokens.spacing.xs
                    }}>
                        {title}
                    </div>
                )}
                <div style={{
                    fontSize: tokens.typography.sizes.sm,
                    color: currentStyle.text,
                    lineHeight: tokens.typography.lineHeights.relaxed
                }}>
                    {children}
                </div>
            </div>
        </div>
    );
};

SystemNotice.propTypes = {
    type: PropTypes.oneOf(['info', 'success', 'warning']),
    children: PropTypes.node.isRequired,
    title: PropTypes.string,
    icon: PropTypes.elementType,
    style: PropTypes.object
};

export default SystemNotice;

