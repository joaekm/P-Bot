import React, { useRef, useEffect, useLayoutEffect } from 'react';
import PropTypes from 'prop-types';
import { tokens } from '../tokens';

/**
 * ChatWindow Component
 * 
 * Komplett chattcontainer med:
 * - Sticky header som visar aktuellt steg
 * - Scrollbart meddelandeområde
 * - Fast inputzon i botten (ActionPanel)
 * 
 * Beteende:
 * - Börjar med minHeight
 * - Växer nedåt när meddelanden läggs till
 * - Stannar vid maxHeight och visar scrollbar
 * - Auto-scrollar till botten vid nya meddelanden
 * 
 * @example
 * <ChatWindow
 *   currentStepNumber={1}
 *   currentStepTitle="Beskriv Behov"
 *   inputZone={<ActionPanel mode="text_input" onTextSubmit={handleSubmit} />}
 * >
 *   <AIAnswerContainer text="Hej!" />
 *   <UserAnswerContainer text="Hej själv!" />
 * </ChatWindow>
 */
const ChatWindow = ({ 
    children,
    inputZone,
    currentStepTitle = null,
    currentStepNumber = null,
    minHeight = '500px',
    maxHeight = 'calc(100vh - 160px)',
    style = {}
}) => {
    const messagesContainerRef = useRef(null);
    const prevChildrenLength = useRef(0);

    // Auto-scroll to bottom when new messages are added
    useLayoutEffect(() => {
        const container = messagesContainerRef.current;
        if (!container) return;
        
        // Count children to detect new messages
        const childCount = React.Children.count(children);
        
        if (childCount > prevChildrenLength.current) {
            // New message added - scroll to bottom
            container.scrollTop = container.scrollHeight;
        }
        
        prevChildrenLength.current = childCount;
    }, [children]);

    return (
        <div 
            style={{
                display: 'flex',
                flexDirection: 'column',
                height: maxHeight, // Use height instead of maxHeight for scroll to work
                minHeight,
                backgroundColor: tokens.colors.neutral.surface,
                borderRadius: tokens.borderRadius.md,
                boxShadow: tokens.shadows.card,
                border: `1px solid ${tokens.colors.neutral.border}`,
                ...style
            }}
        >
            {/* Sticky Header - Current Step */}
            {currentStepTitle && (
                <div 
                    style={{
                        backgroundColor: '#004443', // Dark Petrol (Hardcoded per request)
                        color: tokens.colors.neutral.surface,
                        padding: `${tokens.spacing.md} ${tokens.spacing.xl}`,
                        fontFamily: tokens.typography.fontFamily,
                        fontSize: tokens.typography.sizes.md,
                        fontWeight: tokens.typography.weights.semibold,
                        display: 'flex',
                        alignItems: 'center',
                        gap: tokens.spacing.md,
                        borderBottom: `1px solid rgba(255,255,255,0.1)`,
                        flexShrink: 0,
                        borderTopLeftRadius: tokens.borderRadius.md,
                        borderTopRightRadius: tokens.borderRadius.md,
                    }}
                >
                    {currentStepNumber && (
                        <span 
                            style={{
                                backgroundColor: 'rgba(255,255,255,0.2)',
                                padding: `${tokens.spacing.xs} ${tokens.spacing.md}`,
                                borderRadius: tokens.borderRadius.pill,
                                fontSize: tokens.typography.sizes.sm,
                                fontWeight: tokens.typography.weights.bold
                            }}
                        >
                            Steg {currentStepNumber}
                        </span>
                    )}
                    <span>{currentStepTitle}</span>
                </div>
            )}

            {/* Scrollable Messages Area */}
            <div 
                ref={messagesContainerRef}
                className="adda-chat-scroll-area"
                style={{
                    flex: 1,
                    overflowY: 'auto',
                    overflowX: 'hidden',
                    padding: tokens.spacing['2xl'],
                    display: 'flex',
                    flexDirection: 'column',
                    gap: tokens.spacing.lg,
                    minHeight: 0, // Required for flex overflow to work
                }}
            >
                {children}
            </div>

            {/* Fixed Input Zone at Bottom */}
            <div style={{ paddingBottom: tokens.borderRadius.md }}>
            {inputZone}
            </div>
        </div>
    );
};

ChatWindow.propTypes = {
    /** Chattmeddelanden (AIAnswerContainer, UserAnswerContainer, etc.) */
    children: PropTypes.node,
    /** Inputzon-komponent (ActionPanel) */
    inputZone: PropTypes.node,
    /** Titel för aktuellt steg */
    currentStepTitle: PropTypes.string,
    /** Nummer för aktuellt steg */
    currentStepNumber: PropTypes.number,
    /** Minsta höjd för chattfönstret */
    minHeight: PropTypes.string,
    /** Maxhöjd innan scrollbar visas */
    maxHeight: PropTypes.string,
    /** Extra stilar */
    style: PropTypes.object
};

export default ChatWindow;
