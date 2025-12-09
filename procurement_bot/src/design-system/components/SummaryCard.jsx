import React from 'react';
import PropTypes from 'prop-types';
import { tokens } from '../tokens';
import { Check, Clock, MapPin, Calendar, Banknote, Users, FileText } from 'lucide-react';

/**
 * SummaryCard Component ("Varukorgen") v5.24
 * 
 * Visar en sammanfattning av användarens förfrågan med stöd för
 * FLERA resurser (team-beställningar).
 * 
 * Kanoniska fältnamn (från adda_taxonomy.json):
 * - resources: Array med { id, roll, level, antal, is_complete }
 * - Globala fält: location_text, anbudsomrade, volume, start_date, end_date, takpris, prismodell
 * 
 * @example
 * <SummaryCard 
 *   data={{
 *     resources: [
 *       { id: "res_1", roll: "Projektledare", level: 4, antal: 1, is_complete: true },
 *       { id: "res_2", roll: "Utvecklare", level: null, antal: 2, is_complete: false }
 *     ],
 *     location_text: "Stockholm",
 *     anbudsomrade: "D – Stockholm",
 *     volume: 500,
 *     start_date: "2025-06-01",
 *     takpris: 800000
 *   }}
 * />
 */
const SummaryCard = ({ 
    data = {}, 
    title = "Din Förfrågan",
    style = {} 
}) => {
    // Extract resources array and global fields (v5.24 kanoniska fältnamn)
    const resources = data.resources || [];
    
    // Determine labels based on pricing model
    const isFastPris = data.prismodell === 'FAST_PRIS';
    const moneyLabel = isFastPris ? 'Budget' : 'Takpris';
    const showVolume = !isFastPris || data.volume; // Hide volume for FastPris unless explicitly set

    const globalFields = [
        { key: 'anbudsomrade', label: 'Anbudsområde', icon: MapPin },
        { key: 'location_text', label: 'Plats', icon: MapPin },
        ...(showVolume ? [{ key: 'volume', label: 'Volym', icon: Users, format: (v) => v ? `${v} timmar` : null }] : []),
        { key: 'start_date', label: 'Startdatum', icon: Calendar, format: formatDate },
        { key: 'end_date', label: 'Slutdatum', icon: Calendar, format: formatDate },
        { key: 'takpris', label: moneyLabel, icon: Banknote, format: (v) => v ? `${v.toLocaleString('sv-SE')} kr` : null },
        { key: 'prismodell', label: 'Prismodell', icon: Banknote },
        // New: Show description status
        { 
            key: 'behovsbeskrivning', // Or uppdragsbeskrivning if that's what we use
            label: 'Beskrivning', 
            icon: FileText, 
            format: (v) => v ? '✓ Ifylld' : null 
        }
    ];

    // Check both potential description fields
    const descriptionValue = data.behovsbeskrivning || data.uppdragsbeskrivning;
    // Inject the description value into data for the loop below if not present
    const displayData = { ...data, behovsbeskrivning: descriptionValue };

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

    // Count completed items (v5.24: is_complete istället för status)
    const completedResources = resources.filter(r => r.is_complete || r.status === 'DONE').length;
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
                            // v5.24: stöd för både nya (is_complete, roll, antal) och gamla (status, role, quantity)
                            const isDone = resource.is_complete || resource.status === 'DONE';
                            const quantity = resource.antal || resource.quantity || 1;
                            const roleName = resource.roll || resource.role || 'Okänd';
                            
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
                                            {quantity > 1 ? `${quantity}× ` : ''}{roleName}
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
                                        {resource.level ? `KN ${resource.level}` : 'Nivå?'}
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
                        const rawValue = displayData[field.key];
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

        </div>
    );
};

SummaryCard.propTypes = {
    /** Data object with extracted entities (v5.24 kanoniska fältnamn) */
    data: PropTypes.shape({
        resources: PropTypes.arrayOf(PropTypes.shape({
            id: PropTypes.string,
            roll: PropTypes.string,           // v5.24: roll (tidigare role)
            level: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
            antal: PropTypes.number,          // v5.24: antal (tidigare quantity)
            is_complete: PropTypes.bool,      // v5.24: is_complete (tidigare status)
            // Backward compat
            role: PropTypes.string,
            quantity: PropTypes.number,
            status: PropTypes.oneOf(['DONE', 'PENDING'])
        })),
        location_text: PropTypes.string,      // v5.24: location_text (tidigare location)
        anbudsomrade: PropTypes.string,       // v5.24: nytt fält
        volume: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
        start_date: PropTypes.string,
        end_date: PropTypes.string,           // v5.24: nytt fält
        takpris: PropTypes.number,            // v5.24: takpris (tidigare price_cap)
        prismodell: PropTypes.string,         // v5.24: nytt fält
        // Backward compat
        location: PropTypes.string,
        price_cap: PropTypes.string
    }),
    /** Card title */
    title: PropTypes.string,
    /** Additional styles */
    style: PropTypes.object
};

export default SummaryCard;
