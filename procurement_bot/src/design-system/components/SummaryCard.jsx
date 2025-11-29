import React from 'react';
import PropTypes from 'prop-types';
import { tokens } from '../tokens';
import { Check, Clock, MapPin, Calendar, Banknote, Users, AlertCircle } from 'lucide-react';

/**
 * SummaryCard Component ("Varukorgen")
 * 
 * Visar en sammanfattning av användarens förfrågan med stöd för
 * FLERA resurser (team-beställningar).
 * 
 * Ny struktur:
 * - resources: Array med { id, role, level, quantity, status }
 * - Globala fält: location, volume, start_date, price_cap
 * 
 * @example
 * <SummaryCard 
 *   data={{
 *     resources: [
 *       { id: "res_1", role: "Projektledare", level: 4, quantity: 1, status: "DONE" },
 *       { id: "res_2", role: "Utvecklare", level: null, quantity: 2, status: "PENDING" }
 *     ],
 *     location: "Stockholm",
 *     volume: "500 timmar",
 *     start_date: "2025-06-01",
 *     price_cap: null
 *   }}
 * />
 */
const SummaryCard = ({ 
    data = {}, 
    title = "Din Förfrågan",
    style = {} 
}) => {
    // Extract resources array and global fields
    const resources = data.resources || [];
    const globalFields = [
        { key: 'location', label: 'Plats', icon: MapPin },
        { key: 'volume', label: 'Volym', icon: Users },
        { key: 'start_date', label: 'Startdatum', icon: Calendar, format: formatDate },
        { key: 'price_cap', label: 'Takpris', icon: Banknote }
    ];

    // Format date from YYYY-MM-DD to readable format
    function formatDate(dateStr) {
        if (!dateStr) return null;
        try {
            const date = new Date(dateStr);
            return date.toLocaleDateString('sv-SE', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
            });
        } catch {
            return dateStr;
        }
    }

    // Count completed items
    const completedResources = resources.filter(r => r.status === 'DONE').length;
    const filledGlobals = globalFields.filter(f => data[f.key] !== null && data[f.key] !== undefined).length;
    const totalItems = resources.length + globalFields.length;
    const completedItems = completedResources + filledGlobals;

    // Check if we have any data at all
    const hasData = resources.length > 0 || filledGlobals > 0;

    return (
        <div 
            style={{
                backgroundColor: tokens.colors.neutral.surface,
                borderRadius: tokens.borderRadius.md,
                boxShadow: tokens.shadows.card,
                border: `1px solid ${tokens.colors.neutral.border}`,
                overflow: 'hidden',
                fontFamily: tokens.typography.fontFamily,
                ...style
            }}
        >
            {/* Header */}
            <div 
                style={{
                    backgroundColor: tokens.colors.brand.secondary,
                    color: tokens.colors.neutral.surface,
                    padding: `${tokens.spacing.md} ${tokens.spacing['2xl']}`,
                    fontSize: tokens.typography.sizes.sm,
                    fontWeight: tokens.typography.weights.semibold,
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                }}
            >
                <span>{title}</span>
                {hasData && (
                    <span 
                        style={{
                            backgroundColor: 'rgba(255,255,255,0.2)',
                            padding: `${tokens.spacing.xs} ${tokens.spacing.md}`,
                            borderRadius: tokens.borderRadius.pill,
                            fontSize: tokens.typography.sizes.xs
                        }}
                    >
                        {completedItems}/{totalItems}
                    </span>
                )}
            </div>

            <div style={{ padding: tokens.spacing['2xl'] }}>
                {/* Resources Section */}
                {resources.length > 0 && (
                    <div style={{ marginBottom: tokens.spacing['2xl'] }}>
                        <div 
                            style={{
                                fontSize: tokens.typography.sizes.xs,
                                fontWeight: tokens.typography.weights.semibold,
                                color: tokens.colors.neutral.lightGrey,
                                textTransform: 'uppercase',
                                letterSpacing: '0.5px',
                                marginBottom: tokens.spacing.md
                            }}
                        >
                            Resurser ({resources.length})
                        </div>
                        
                        {resources.map((resource, index) => {
                            const isDone = resource.status === 'DONE';
                            const quantity = resource.quantity || 1;
                            
                            return (
                                <div 
                                    key={resource.id || index}
                                    style={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center',
                                        padding: `${tokens.spacing.md} 0`,
                                        borderBottom: index < resources.length - 1 
                                            ? `1px solid ${tokens.colors.neutral.border}` 
                                            : 'none'
                                    }}
                                >
                                    {/* Left: Status + Role */}
                                    <div 
                                        style={{
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: tokens.spacing.md
                                        }}
                                    >
                                        {/* Status Icon */}
                                        <div 
                                            style={{
                                                width: '20px',
                                                height: '20px',
                                                borderRadius: '50%',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                backgroundColor: isDone 
                                                    ? tokens.colors.status.successBg 
                                                    : tokens.colors.status.warningBg,
                                                flexShrink: 0
                                            }}
                                        >
                                            {isDone ? (
                                                <Check 
                                                    size={12} 
                                                    color={tokens.colors.status.successDark} 
                                                    strokeWidth={3}
                                                />
                                            ) : (
                                                <Clock 
                                                    size={12} 
                                                    color={tokens.colors.status.warningDark}
                                                />
                                            )}
                                        </div>
                                        
                                        {/* Role + Quantity */}
                                        <span 
                                            style={{
                                                fontSize: tokens.typography.sizes.sm,
                                                fontWeight: tokens.typography.weights.medium,
                                                color: tokens.colors.neutral.text
                                            }}
                                        >
                                            {quantity > 1 ? `${quantity}× ` : ''}{resource.role}
                                        </span>
                                    </div>

                                    {/* Right: Level */}
                                    <span 
                                        style={{
                                            fontSize: tokens.typography.sizes.sm,
                                            fontWeight: isDone 
                                                ? tokens.typography.weights.semibold 
                                                : tokens.typography.weights.regular,
                                            color: isDone 
                                                ? tokens.colors.brand.secondary 
                                                : tokens.colors.neutral.lightGrey,
                                            fontStyle: isDone ? 'normal' : 'italic',
                                            backgroundColor: isDone 
                                                ? tokens.colors.brand.lightTint 
                                                : 'transparent',
                                            padding: isDone 
                                                ? `${tokens.spacing.xs} ${tokens.spacing.md}` 
                                                : '0',
                                            borderRadius: tokens.borderRadius.sm
                                        }}
                                    >
                                        {resource.level ? `Nivå ${resource.level}` : 'Nivå?'}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                )}

                {/* Empty State for Resources */}
                {resources.length === 0 && (
                    <div 
                        style={{
                            textAlign: 'center',
                            padding: `${tokens.spacing['2xl']} 0`,
                            color: tokens.colors.neutral.lightGrey,
                            fontSize: tokens.typography.sizes.sm,
                            fontStyle: 'italic'
                        }}
                    >
                        Inga resurser tillagda än
                    </div>
                )}

                {/* Divider */}
                {resources.length > 0 && (
                    <div 
                        style={{
                            height: '1px',
                            backgroundColor: tokens.colors.neutral.border,
                            margin: `${tokens.spacing.md} 0`
                        }}
                    />
                )}

                {/* Global Fields */}
                <div>
                    {globalFields.map((field, index) => {
                        const rawValue = data[field.key];
                        const value = field.format ? field.format(rawValue) : rawValue;
                        const isFilled = value !== null && value !== undefined;
                        const Icon = field.icon;

                        return (
                            <div 
                                key={field.key}
                                style={{
                                    display: 'flex',
                                    justifyContent: 'space-between',
                                    alignItems: 'center',
                                    padding: `${tokens.spacing.sm} 0`
                                }}
                            >
                                {/* Label with Icon */}
                                <div 
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: tokens.spacing.md
                                    }}
                                >
                                    <Icon 
                                        size={14} 
                                        color={isFilled 
                                            ? tokens.colors.brand.secondary 
                                            : tokens.colors.neutral.lightGrey
                                        }
                                    />
                                    <span 
                                        style={{
                                            fontSize: tokens.typography.sizes.xs,
                                            color: tokens.colors.neutral.lightGrey
                                        }}
                                    >
                                        {field.label}
                                    </span>
                                </div>

                                {/* Value */}
                                <span 
                                    style={{
                                        fontSize: tokens.typography.sizes.xs,
                                        fontWeight: isFilled 
                                            ? tokens.typography.weights.medium 
                                            : tokens.typography.weights.regular,
                                        color: isFilled 
                                            ? tokens.colors.neutral.text 
                                            : tokens.colors.neutral.lightGrey,
                                        fontStyle: isFilled ? 'normal' : 'italic'
                                    }}
                                >
                                    {isFilled ? value : '—'}
                                </span>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* Footer - Pending Resources Hint */}
            {resources.some(r => r.status === 'PENDING') && (
                <div 
                    style={{
                        backgroundColor: tokens.colors.status.warningBg,
                        padding: `${tokens.spacing.md} ${tokens.spacing['2xl']}`,
                        fontSize: tokens.typography.sizes.xs,
                        color: tokens.colors.status.warningDark,
                        display: 'flex',
                        alignItems: 'center',
                        gap: tokens.spacing.md
                    }}
                >
                    <AlertCircle size={14} />
                    <span>Ange kompetensnivå för markerade resurser</span>
                </div>
            )}
        </div>
    );
};

SummaryCard.propTypes = {
    /** Data object with extracted entities (multi-resource format) */
    data: PropTypes.shape({
        resources: PropTypes.arrayOf(PropTypes.shape({
            id: PropTypes.string,
            role: PropTypes.string,
            level: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
            quantity: PropTypes.number,
            status: PropTypes.oneOf(['DONE', 'PENDING'])
        })),
        location: PropTypes.string,
        volume: PropTypes.string,
        start_date: PropTypes.string,
        price_cap: PropTypes.string
    }),
    /** Card title */
    title: PropTypes.string,
    /** Additional styles */
    style: PropTypes.object
};

export default SummaryCard;
