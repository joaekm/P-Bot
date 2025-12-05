import React from 'react';
import PropTypes from 'prop-types';
import { tokens } from '../tokens';
import { Check, Clock, MapPin, Calendar, Banknote, Users, AlertCircle, Globe, FileText, Scale, Shield, UserCheck, Zap } from 'lucide-react';

/**
 * SummaryCard Component ("Varukorgen")
 * 
 * Visar en sammanfattning av användarens förfrågan med stöd för
 * FLERA resurser (team-beställningar).
 * 
 * Struktur (matchar backend AvropsData):
 * - resources: Array med { id, roll, level, antal, is_complete }
 * - Globala fält: anbudsomrade, location_text, volume, start_date, end_date, takpris
 * - FKU-fält (visas om avrop_typ börjar med "FKU"): prismodell, utvarderingsmodell, uppdragsbeskrivning
 * - Flaggor (visas om true): hanterar_personuppgifter, sakerhetsklassad
 * - avrop_typ: Visar DR/FKU badge
 * 
 * @example
 * <SummaryCard 
 *   data={{
 *     avrop_typ: "FKU_RESURS",
 *     resources: [
 *       { id: "res_1", roll: "Projektledare", level: 5, antal: 1, is_complete: true }
 *     ],
 *     anbudsomrade: "D - Stockholm",
 *     location_text: "Stockholm",
 *     volume: 500,
 *     start_date: "2025-06-01",
 *     end_date: "2025-12-31",
 *     takpris: 1500,
 *     prismodell: "LOPANDE_MED_TAK",
 *     utvarderingsmodell: "PRIS_70_KVALITET_30",
 *     hanterar_personuppgifter: true
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
    const isFKU = data.avrop_typ && data.avrop_typ.startsWith('FKU');
    
    // Base global fields (always shown)
    const globalFields = [
        { key: 'anbudsomrade', label: 'Anbudsområde', icon: Globe },
        { key: 'location_text', label: 'Plats', icon: MapPin },
        { key: 'volume', label: 'Volym', icon: Users, format: (v) => v ? `${v} timmar` : null },
        { key: 'start_date', label: 'Startdatum', icon: Calendar, format: formatDate },
        { key: 'end_date', label: 'Slutdatum', icon: Calendar, format: formatDate },
        { key: 'takpris', label: 'Takpris', icon: Banknote, format: (v) => v ? `${v} kr/h` : null }
    ];
    
    // FKU-specific fields (only shown when avrop_typ is FKU)
    const fkuFields = isFKU ? [
        { key: 'prismodell', label: 'Prismodell', icon: Banknote, format: formatPrismodell },
        { key: 'utvarderingsmodell', label: 'Utvärderingsmodell', icon: Scale, format: formatUtvardering },
        { key: 'uppdragsbeskrivning', label: 'Uppdragsbeskrivning', icon: FileText, format: (v) => v ? '✓ Angiven' : null }
    ] : [];
    
    // Conditional flags (only shown when true)
    const flagFields = [
        data.hanterar_personuppgifter && { key: 'hanterar_personuppgifter', label: 'Personuppgifter', icon: UserCheck, format: () => 'Ja, hanteras' },
        data.sakerhetsklassad && { key: 'sakerhetsklassad', label: 'Säkerhetsklassad', icon: Shield, format: () => 'Ja' }
    ].filter(Boolean);
    
    // Combine all fields
    const allFields = [...globalFields, ...fkuFields, ...flagFields];

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
    
    // Format prismodell enum to readable text
    function formatPrismodell(val) {
        if (!val) return null;
        const labels = {
            'LOPANDE': 'Löpande räkning',
            'FAST_PRIS': 'Fast pris',
            'LOPANDE_MED_TAK': 'Löpande med tak'
        };
        return labels[val] || val;
    }
    
    // Format utvarderingsmodell enum to readable text
    function formatUtvardering(val) {
        if (!val) return null;
        const labels = {
            'PRIS_100': '100% pris',
            'PRIS_70_KVALITET_30': '70% pris, 30% kvalitet',
            'PRIS_50_KVALITET_50': '50% pris, 50% kvalitet'
        };
        return labels[val] || val;
    }
    
    // Format avrop_typ for display
    function formatAvropsTyp(val) {
        if (!val) return null;
        const labels = {
            'DR_RESURS': 'Dynamisk Rangordning',
            'FKU_RESURS': 'FKU - Resurs',
            'FKU_PROJEKT': 'FKU - Projekt'
        };
        return labels[val] || val;
    }

    // Count completed items (is_complete from backend)
    const completedResources = resources.filter(r => r.is_complete).length;
    const filledGlobals = allFields.filter(f => data[f.key] !== null && data[f.key] !== undefined).length;
    const totalItems = resources.length + allFields.length;
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
                <div style={{ display: 'flex', alignItems: 'center', gap: tokens.spacing.md }}>
                    <span>{title}</span>
                    {data.avrop_typ && (
                        <span 
                            style={{
                                backgroundColor: isFKU ? tokens.colors.status.warningBg : tokens.colors.status.successBg,
                                color: isFKU ? tokens.colors.status.warningDark : tokens.colors.status.successDark,
                                padding: `${tokens.spacing.xs} ${tokens.spacing.sm}`,
                                borderRadius: tokens.borderRadius.sm,
                                fontSize: tokens.typography.sizes.xs,
                                fontWeight: tokens.typography.weights.medium,
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px'
                            }}
                        >
                            <Zap size={10} />
                            {isFKU ? 'FKU' : 'DR'}
                        </span>
                    )}
                </div>
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
                            const isDone = resource.is_complete;
                            const antal = resource.antal || 1;
                            
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
                                    {/* Left: Status + Roll */}
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
                                        
                                        {/* Roll + Antal */}
                                        <span 
                                            style={{
                                                fontSize: tokens.typography.sizes.sm,
                                                fontWeight: tokens.typography.weights.medium,
                                                color: tokens.colors.neutral.text
                                            }}
                                        >
                                            {antal > 1 ? `${antal}× ` : ''}{resource.roll}
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
                                        {resource.level ? `Kompetensnivå ${resource.level}` : 'Nivå?'}
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
                    {allFields.map((field, index) => {
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
            {resources.some(r => !r.is_complete) && (
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
    /** Data object matching backend AvropsData */
    data: PropTypes.shape({
        resources: PropTypes.arrayOf(PropTypes.shape({
            id: PropTypes.string,
            roll: PropTypes.string,
            level: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
            antal: PropTypes.number,
            is_complete: PropTypes.bool
        })),
        anbudsomrade: PropTypes.string,
        location_text: PropTypes.string,
        volume: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
        start_date: PropTypes.string,
        end_date: PropTypes.string,
        takpris: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
        // FKU-specific
        avrop_typ: PropTypes.string,
        prismodell: PropTypes.string,
        utvarderingsmodell: PropTypes.string,
        uppdragsbeskrivning: PropTypes.string,
        // Flags
        hanterar_personuppgifter: PropTypes.bool,
        sakerhetsklassad: PropTypes.bool
    }),
    /** Card title */
    title: PropTypes.string,
    /** Additional styles */
    style: PropTypes.object
};

export default SummaryCard;
