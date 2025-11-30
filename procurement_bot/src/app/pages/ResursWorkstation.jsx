import React, { useState, useEffect, useRef, memo } from 'react';
import '../../PBotMain.css'; 
import {
  tokens,
  LayoutSidebarRight,
  AddaCard,
  BodyText,
  AIAnswerContainer,
  UserAnswerContainer,
  SystemNotice,
  ProcessProgressBar,
  ChatWindow,
  StepTransitionNotice,
  ActionPanel,
  SummaryCard
} from '../../design-system';
import { getWidgetComponent } from '../../utils/componentRegistry';

// =============================================================================
// SERVER-DRIVEN UI ARCHITECTURE (v3.1)
// =============================================================================
// All UI is controlled by the backend via the AIResponse schema:
// - text_content: The AI's message
// - stream_widget: Optional widget to render in chat
// - action_panel: Controls the input zone (mode, placeholder, actions)
// - session_state: Persistent state with resource_manifest
// - is_step_complete: Whether to advance to next step
// =============================================================================

// --- Step Metadata ---
const STEP_METADATA = {
  step_1_needs: { title: 'Beskriv Behov', process_step: 1 },
  step_2_level: { title: 'Bedöm Kompetensnivå', process_step: 2 },
  step_3_volume: { title: 'Volym & Pris', process_step: 3 },
  step_4_strategy: { title: 'Avropsform & Strategi', process_step: 4 },
};

// --- AI Message Component ---
const AIMessage = memo(({ text, streamWidget }) => {
  return (
    <>
      {text && <AIAnswerContainer text={text} />}
      {streamWidget && <StreamWidget widget={streamWidget} />}
    </>
  );
});

// --- Stream Widget Renderer ---
const StreamWidget = ({ widget }) => {
  if (!widget || !widget.widget_type) return null;
  
  const Component = getWidgetComponent(widget.widget_type);
  
  if (!Component) {
    // Fallback: show debug info for unknown widgets
    return (
      <div style={{
        backgroundColor: '#FEF3C7',
        border: '1px dashed #F59E0B',
        borderRadius: tokens.borderRadius.md,
        padding: tokens.spacing.md,
        marginTop: tokens.spacing.sm,
        fontSize: tokens.typography.sizes.sm,
        fontFamily: 'monospace',
      }}>
        Unknown widget: {widget.widget_type}
        <pre>{JSON.stringify(widget.props, null, 2)}</pre>
      </div>
    );
  }
  
  return <Component {...widget.props} />;
};

// =============================================================================
// MAIN COMPONENT
// =============================================================================

export default function ResursWorkstation() {
  // --- State ---
  const [chatMessages, setChatMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Session state (from backend)
  // Includes source_documents for session-based data (private, not in ChromaDB)
  const [sessionState, setSessionState] = useState({
    resource_manifest: [],
    source_documents: [],  // Uploaded documents with full text
    metadata: {},
    current_step: 'step_1_needs'
  });
  
  // Action panel state (from backend)
  const [actionPanel, setActionPanel] = useState({
    mode: 'text_input',
    placeholder: 'Beskriv ditt behov...',
    actions: []
  });
  
  // Track step transitions
  const [previousStep, setPreviousStep] = useState('step_1_needs');
  
  // UI Directives from backend (Chunk 3: Data Layer)
  const [summaryData, setSummaryData] = useState({});           // entity_summary
  const [headerTitle, setHeaderTitle] = useState('Resursupphandling');  // sticky header title
  const [activeStep, setActiveStep] = useState('step_1_needs'); // process step from backend
  const [missingInfo, setMissingInfo] = useState([]);           // what's still needed
  const [currentIntent, setCurrentIntent] = useState('INSPIRATION');  // FACT or INSPIRATION
  
  // Guard against double initialization in React Strict Mode
  const initializedRef = useRef(false);

  // --- Initialize conversation ---
  useEffect(() => {
    if (initializedRef.current) return;
    initializedRef.current = true;
    initializeConversation();
  }, []);

  // --- Track step transitions ---
  useEffect(() => {
    const currentStep = sessionState.current_step;
    if (currentStep !== previousStep) {
      const fromMeta = STEP_METADATA[previousStep];
      const toMeta = STEP_METADATA[currentStep];
      
      if (fromMeta && toMeta && fromMeta.process_step < toMeta.process_step) {
        setChatMessages(prev => [...prev, {
          type: 'transition',
          fromStep: fromMeta.process_step,
          fromStepTitle: fromMeta.title,
          toStep: toMeta.process_step,
          toStepTitle: toMeta.title,
          id: Date.now()
        }]);
      }
      setPreviousStep(currentStep);
    }
  }, [sessionState.current_step, previousStep]);

  // --- API Functions ---
  const initializeConversation = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/conversation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_message: null,
          conversation_history: [],
          session_state: sessionState
        })
      });
      
      if (!response.ok) throw new Error('Failed to initialize');
      
      const data = await response.json();
      handleAIResponse(data);
      
    } catch (error) {
      console.error('Failed to initialize:', error);
      // Fallback message
      setChatMessages([{
        type: 'ai',
        text: 'Hej! Beskriv vilka konsulter du behöver, eller ladda upp ett underlag.',
        streamWidget: null,
        id: Date.now()
      }]);
    }
    setIsLoading(false);
  };

  const sendMessage = async (message) => {
    // Add user message
    setChatMessages(prev => [...prev, { type: 'user', text: message, id: Date.now() }]);
    
    // Build conversation history
    const history = chatMessages
      .filter(m => m.type === 'user' || m.type === 'ai')
      .map(m => ({
        role: m.type === 'user' ? 'user' : 'assistant',
        content: m.text
      }));
    
    setIsLoading(true);
    setActionPanel(prev => ({ ...prev, mode: 'locked' }));
    
    try {
      const response = await fetch('/api/conversation', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_message: message,
          conversation_history: history,
          session_state: sessionState
        })
      });
      
      if (!response.ok) throw new Error('Request failed');
      
      const data = await response.json();
      handleAIResponse(data);
      
    } catch (error) {
      console.error('Error sending message:', error);
      setChatMessages(prev => [...prev, {
        type: 'error',
        text: 'Kunde inte få svar. Försök igen.',
        id: Date.now()
      }]);
      // Restore action panel
      setActionPanel({
        mode: 'text_input',
        placeholder: 'Försök igen...',
        actions: []
      });
    }
    setIsLoading(false);
  };

  const handleAIResponse = (data) => {
    // Add AI message (backend sends 'message', not 'text_content')
    if (data.message) {
      setChatMessages(prev => [...prev, {
        type: 'ai',
        text: data.message,
        streamWidget: data.stream_widget || null,
        id: Date.now()
      }]);
    }
    
    // Update session state
    if (data.session_state) {
      setSessionState(data.session_state);
    }
    
    // Handle UI Directives from backend (Chunk 3: Data Layer)
    if (data.ui_directives) {
      console.log('📦 UI Directives received:', data.ui_directives);
      
      const { 
        entity_summary, 
        update_sticky_header, 
        set_active_process_step,
        missing_info,
        current_intent 
      } = data.ui_directives;
      
      if (entity_summary) {
        setSummaryData(entity_summary);
        console.log('🎯 Entity Summary:', entity_summary);
      }
      if (update_sticky_header) {
        setHeaderTitle(update_sticky_header);
      }
      if (set_active_process_step) {
        setActiveStep(set_active_process_step);
      }
      if (missing_info) {
        setMissingInfo(missing_info);
      }
      if (current_intent) {
        setCurrentIntent(current_intent);
      }
    }
    
    // Update action panel from backend, or use input_placeholder for simple responses
    if (data.action_panel) {
      setActionPanel(data.action_panel);
    } else if (data.input_placeholder) {
      setActionPanel(prev => ({
        ...prev,
        mode: 'text_input',
        placeholder: data.input_placeholder
      }));
    } else {
      // Restore default input mode after response
      setActionPanel({
        mode: 'text_input',
        placeholder: 'Skriv här...',
        actions: []
      });
    }
  };

  const handleTextSubmit = (text) => {
    sendMessage(text);
  };

  const handleActionClick = (actionValue) => {
    // Find the action label for display
    const action = actionPanel.actions.find(a => a.value === actionValue);
    const displayText = action ? action.label : actionValue;
    sendMessage(displayText);
  };

  const handleFileUpload = async (file) => {
    // Add uploading message
    setChatMessages(prev => [...prev, {
      type: 'user',
      text: `📎 Laddar upp ${file.name}...`,
      id: Date.now()
    }]);
    
    setIsLoading(true);
    setActionPanel(prev => ({ ...prev, mode: 'locked' }));
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await fetch('/api/analyze-document', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) throw new Error('Upload failed');
      
      const data = await response.json();
      
      // Update user message to success
      setChatMessages(prev => {
        const updated = [...prev];
        const lastUserIdx = updated.findLastIndex(m => m.type === 'user');
        if (lastUserIdx >= 0) {
          updated[lastUserIdx] = { ...updated[lastUserIdx], text: `✓ ${file.name} analyserad` };
        }
        return updated;
      });
      
      // Build updated session state with source_document
      // This is the Hybrid Model: source_documents are session-private, NOT in ChromaDB
      let updatedSessionState = { ...sessionState };
      
      // Add source_document to session (stores full text for context in later steps)
      if (data.source_document) {
        updatedSessionState = {
          ...updatedSessionState,
          source_documents: [...updatedSessionState.source_documents, data.source_document]
        };
      }
      
      // Update session state with extracted resources
      if (data.resources && data.resources.length > 0) {
        const resources = data.resources.map((r, i) => ({
          role: r.role,
          quantity: r.quantity || 1,
          location: r.location || null,
          level: null,
          hours: null,
          estimated_cost: null,
          source: 'document'
        }));
        
        updatedSessionState = {
          ...updatedSessionState,
          resource_manifest: resources
        };
        
        // Set the updated state
        setSessionState(updatedSessionState);
        
        // Send summary to AI with the updated session state
        const summary = data.summary || resources.map(r => `${r.quantity}x ${r.role}`).join(', ');
        
        // Build conversation history
        const history = chatMessages
          .filter(m => m.type === 'user' || m.type === 'ai')
          .map(m => ({
            role: m.type === 'user' ? 'user' : 'assistant',
            content: m.text
          }));
        
        // Add uploading message to history
        history.push({ role: 'user', content: `Jag har laddat upp ett dokument. Hittade: ${summary}` });
        
        // Add user message to chat
        setChatMessages(prev => [...prev, { 
          type: 'user', 
          text: `Jag har laddat upp ett dokument. Hittade: ${summary}`, 
          id: Date.now() 
        }]);
        
        // Call AI with the updated session state (including source_documents)
        const aiResponse = await fetch('/api/conversation', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_message: `Jag har laddat upp ett dokument. Hittade: ${summary}`,
            conversation_history: history,
            session_state: updatedSessionState
          })
        });
        
        if (aiResponse.ok) {
          const aiData = await aiResponse.json();
          handleAIResponse(aiData);
        }
      } else {
        // No resources found, but still store the document
        setSessionState(updatedSessionState);
        
        // Ask AI to analyze
        const history = chatMessages
          .filter(m => m.type === 'user' || m.type === 'ai')
          .map(m => ({
            role: m.type === 'user' ? 'user' : 'assistant',
            content: m.text
          }));
        
        setChatMessages(prev => [...prev, { 
          type: 'user', 
          text: 'Jag har laddat upp ett dokument men inga roller kunde extraheras automatiskt.', 
          id: Date.now() 
        }]);
        
        const aiResponse = await fetch('/api/conversation', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_message: 'Jag har laddat upp ett dokument men inga roller kunde extraheras automatiskt.',
            conversation_history: history,
            session_state: updatedSessionState
          })
        });
        
        if (aiResponse.ok) {
          const aiData = await aiResponse.json();
          handleAIResponse(aiData);
        }
      }
      
    } catch (error) {
      console.error('Upload error:', error);
      setChatMessages(prev => [...prev, {
        type: 'error',
        text: 'Kunde inte analysera dokumentet. Försök igen.',
        id: Date.now()
      }]);
      setActionPanel({
        mode: 'text_input',
        placeholder: 'Försök igen...',
        actions: []
      });
    }
    setIsLoading(false);
  };

  // --- Calculate current step info from activeStep (from backend) ---
  // Map activeStep to process step index
  const stepMapping = {
    'step_1_intake': 0,
    'step_1_needs': 0,
    'step_2_level': 1,
    'step_3_volume': 2,
    'step_4_strategy': 3,
    'general': 0
  };
  const currentStepIndex = stepMapping[activeStep] ?? 0;
  
  // Process steps for progress bar
  const processSteps = [
    { id: 1, title: 'Beskriv Behov' },
    { id: 2, title: 'Bedöm Kompetensnivå' },
    { id: 3, title: 'Volym & Pris' },
    { id: 4, title: 'Avropsform & Strategi' }
  ];

  // --- Sidebar ---
  const sidebarContent = (
    <>
      {/* Progress Bar */}
      <AddaCard style={{ marginBottom: tokens.spacing['2xl'], padding: tokens.spacing['2xl'] }}>
      <ProcessProgressBar 
        steps={processSteps} 
          currentStepIndex={currentStepIndex}
        />
      </AddaCard>
      
      {/* Summary Card (Varukorgen) */}
      <SummaryCard 
        data={summaryData} 
        title="Din Förfrågan"
        style={{ marginBottom: tokens.spacing['2xl'] }}
      />
      
      {/* Information Card */}
      <AddaCard bgColor="#FFF" style={{ padding: tokens.spacing['2xl'] }}>
        <BodyText size="sm" bold>Information</BodyText>
        <BodyText size="xs" style={{ fontWeight: 'bold', marginBottom: '8px' }}>
          Så här behandlar vi din information och uppladdade filer.
        </BodyText>
        <BodyText size="xs">
          Kom ihåg att AI ibland kan lämna fel information och att du som avropande part alltid är skyldig att lämna rätt uppgifter och är ansvarig för inlämnade underlag.
        </BodyText>
      </AddaCard>
      
      {/* Debug: Show session state and UI directives */}
      {process.env.NODE_ENV === 'development' && (
        <AddaCard bgColor="#FEF3C7" style={{ padding: tokens.spacing.md, marginTop: tokens.spacing.lg }}>
          <BodyText size="xs" bold>Debug: UI Directives</BodyText>
          <pre style={{ fontSize: '10px', overflow: 'auto', maxHeight: '200px' }}>
            {JSON.stringify({
              ui_directives: {
                headerTitle,
                activeStep,
                currentIntent,
                missingInfo,
                summaryData
              },
              session_state: {
              current_step: sessionState.current_step,
              resource_manifest: sessionState.resource_manifest,
                source_documents: sessionState.source_documents?.length || 0
              }
            }, null, 2)}
          </pre>
        </AddaCard>
      )}
    </>
  );

  // --- Action Panel (Server-Driven) ---
  const inputZone = (
    <ActionPanel
      mode={actionPanel.mode}
      placeholder={actionPanel.placeholder}
      actions={actionPanel.actions}
      onTextSubmit={handleTextSubmit}
      onActionClick={handleActionClick}
      onFileUpload={activeStep === 'step_1_needs' || activeStep === 'step_1_intake' ? handleFileUpload : undefined}
      disabled={isLoading}
      isLoading={isLoading}
    />
  );

  return (
    <LayoutSidebarRight sidebar={sidebarContent}>
      <ChatWindow
        currentStepNumber={currentStepIndex + 1}
        currentStepTitle={headerTitle}
        inputZone={inputZone}
        minHeight="500px"
      >
        {chatMessages.map((msg) => {
          if (msg.type === 'ai') {
            return <AIMessage key={msg.id} text={msg.text} streamWidget={msg.streamWidget} />;
          }
          
          if (msg.type === 'user') {
            return <UserAnswerContainer key={msg.id} text={msg.text} />;
          }
          
          if (msg.type === 'transition') {
            return (
              <StepTransitionNotice
                key={msg.id}
                fromStep={msg.fromStep}
                fromStepTitle={msg.fromStepTitle}
                toStep={msg.toStep}
                toStepTitle={msg.toStepTitle}
              />
            );
          }
          
          if (msg.type === 'error') {
            return <SystemNotice key={msg.id} type="warning">{msg.text}</SystemNotice>;
          }
          
          return null;
        })}

      </ChatWindow>
    </LayoutSidebarRight>
  );
}
