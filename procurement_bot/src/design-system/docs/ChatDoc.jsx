import React, { useState } from 'react';
import { tokens } from '../tokens';
import ChatWindow from '../chat/ChatWindow';
import AIAnswerContainer from '../chat/AIAnswerContainer';
import UserAnswerContainer from '../chat/UserAnswerContainer';
import StepTransitionNotice from '../chat/StepTransitionNotice';
import ActionPanel from '../chat/ActionPanel';
import ProcessProgressBar from '../components/ProcessProgressBar';

const ChatDoc = () => {
  const [demoMessages, setDemoMessages] = useState([
    { type: 'ai', text: 'Hej! Jag är din AI-assistent. Hur kan jag hjälpa dig?' },
  ]);
  const [actionMode, setActionMode] = useState('text_input');

  const handleDemoSubmit = (text) => {
    setDemoMessages(prev => [
      ...prev,
      { type: 'user', text },
      { type: 'ai', text: `Du skrev: "${text}". Det är ett bra meddelande!` }
    ]);
  };

  return (
    <div>
      <h2 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '24px' }}>Chattkomponenter</h2>
      <p style={{ color: '#666', marginBottom: '32px' }}>
        Specialiserade komponenter för konversationsgränssnitt. Dessa komponenter bygger tillsammans ett komplett chattgränssnitt.
      </p>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
        
        {/* ChatWindow - Full Demo */}
        <section style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>ChatWindow</h3>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>
            Huvudcontainer för chatten. Innehåller header med stegindikator, scrollbart meddelandeområde och fast inputzon i botten.
          </p>
          
          <div style={{ backgroundColor: tokens.colors.neutral.bg, padding: '16px', borderRadius: '8px' }}>
            <ChatWindow
              currentStepNumber={1}
              currentStepTitle="Demo: Beskriv Behov"
              minHeight="300px"
              maxHeight="400px"
              inputZone={
                <ActionPanel
                  mode="text_input"
                  placeholder="Skriv ett testmeddelande..."
                  onTextSubmit={handleDemoSubmit}
                />
              }
            >
              {demoMessages.map((msg, i) => (
                msg.type === 'ai' 
                  ? <AIAnswerContainer key={i} text={msg.text} />
                  : <UserAnswerContainer key={i} text={msg.text} />
              ))}
            </ChatWindow>
              </div>
          
          <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#F5F5F5', borderRadius: '8px', fontFamily: 'monospace', fontSize: '12px' }}>
            <strong>Props:</strong> currentStepNumber, currentStepTitle, minHeight, maxHeight, inputZone, children
          </div>
        </section>

        {/* AIAnswerContainer */}
        <section style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>AIAnswerContainer</h3>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>
            Pratbubbla för AI-svar. Vänsterställd med ljusblå bakgrund. Stödjer Markdown-formatering.
          </p>
          
          <div style={{ backgroundColor: tokens.colors.neutral.bg, padding: '16px', borderRadius: '8px' }}>
            <AIAnswerContainer text="Hej! Jag kan hjälpa dig med **upphandling** av konsulter. Berätta vad du behöver så guidar jag dig genom processen." />
          </div>
          
          <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#F5F5F5', borderRadius: '8px', fontFamily: 'monospace', fontSize: '12px' }}>
            <strong>Props:</strong> text (string, stödjer Markdown), avatar (optional), children (optional)
          </div>
        </section>

        {/* UserAnswerContainer */}
        <section style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>UserAnswerContainer</h3>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>
            Pratbubbla för användarens meddelanden. Högerställd med gul bakgrund.
          </p>
          
          <div style={{ backgroundColor: tokens.colors.neutral.bg, padding: '16px', borderRadius: '8px' }}>
            <UserAnswerContainer text="Jag behöver 2 st Javautvecklare i Stockholm." />
          </div>
          
          <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#F5F5F5', borderRadius: '8px', fontFamily: 'monospace', fontSize: '12px' }}>
            <strong>Props:</strong> text (string), children (optional)
          </div>
        </section>

        {/* ActionPanel */}
        <section style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>ActionPanel</h3>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>
            Server-driven inputzon. Stödjer flera lägen: textinput, binära val, filuppladdning och låst läge.
          </p>
          
          <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', flexWrap: 'wrap' }}>
            {['text_input', 'binary_choice', 'file_upload', 'locked'].map(mode => (
              <button
                key={mode}
                onClick={() => setActionMode(mode)}
                style={{
                  padding: '8px 16px',
                  borderRadius: '20px',
                  border: 'none',
                  backgroundColor: actionMode === mode ? tokens.colors.brand.primary : '#E5E5E5',
                  color: actionMode === mode ? '#FFF' : '#333',
                  cursor: 'pointer',
                  fontSize: '13px'
                }}
              >
                {mode}
              </button>
            ))}
          </div>
          
          <div style={{ backgroundColor: tokens.colors.neutral.bg, padding: '0', borderRadius: '8px', overflow: 'hidden', border: `1px solid ${tokens.colors.neutral.border}` }}>
            <ActionPanel
              mode={actionMode}
              placeholder="Skriv ditt meddelande här..."
              actions={[
                { label: 'Ja, det stämmer', value: 'yes' },
                { label: 'Nej, ändra', value: 'no' }
              ]}
              onTextSubmit={(text) => alert(`Skickade: ${text}`)}
              onActionClick={(value) => alert(`Valde: ${value}`)}
              onFileUpload={(file) => alert(`Fil: ${file.name}`)}
            />
          </div>
          
          <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#F5F5F5', borderRadius: '8px', fontFamily: 'monospace', fontSize: '12px' }}>
            <strong>Props:</strong> mode ('text_input' | 'binary_choice' | 'file_upload' | 'locked'), placeholder, actions[], onTextSubmit, onActionClick, onFileUpload, disabled, isLoading
          </div>
        </section>

        {/* StepTransitionNotice */}
        <section style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>StepTransitionNotice</h3>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>
            Grön notis som visas i chatten vid byte av processteg.
          </p>
          
          <div style={{ backgroundColor: tokens.colors.neutral.bg, padding: '16px', borderRadius: '8px' }}>
            <StepTransitionNotice 
              fromStep={1}
              fromStepTitle="Behovsinsamling"
              toStep={2}
              toStepTitle="Bedöm Kompetensnivå"
            />
          </div>
          
          <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#F5F5F5', borderRadius: '8px', fontFamily: 'monospace', fontSize: '12px' }}>
            <strong>Props:</strong> fromStep, fromStepTitle, toStep, toStepTitle
          </div>
        </section>

        {/* ProcessProgressBar (Moved from ComponentsDoc) */}
        <section style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>ProcessProgressBar</h3>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>
            Vertikal förloppsindikator för sidopanelen.
          </p>
          
          <div style={{ backgroundColor: tokens.colors.neutral.bg, padding: '16px', borderRadius: '8px', width: '320px' }}>
            <div style={{ backgroundColor: '#FFFFFF', padding: '16px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' }}>
              <ProcessProgressBar 
                steps={[
                  { id: 1, title: 'Beskriv Behov' },
                  { id: 2, title: 'Bedöm Kompetensnivå' },
                  { id: 3, title: 'Volym & Pris' },
                  { id: 4, title: 'Avropsform & Strategi' }
                ]} 
                currentStepIndex={1} 
              />
            </div>
          </div>
          
          <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#F5F5F5', borderRadius: '8px', fontFamily: 'monospace', fontSize: '12px' }}>
            <strong>Props:</strong> steps[], currentStepIndex, style
          </div>
        </section>

        {/* Conversation Example */}
        <section style={{ backgroundColor: '#FFFFFF', padding: '24px', borderRadius: '12px', boxShadow: tokens.shadows.card, border: '1px solid #E5E5E5' }}>
          <h3 style={{ fontWeight: 'bold', marginBottom: '16px', fontSize: '12px', color: '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Komplett konversationsexempel</h3>
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '16px' }}>
            Visar hur komponenterna används tillsammans i ett typiskt chattflöde.
          </p>
          
          <div style={{ 
            backgroundColor: tokens.colors.neutral.bg, 
            padding: '16px', 
            borderRadius: '8px',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px'
          }}>
            <AIAnswerContainer text="Hej! Jag är Addas digitala avropsassistent. Beskriv ditt behov eller ladda upp ett underlag." />
            
            <UserAnswerContainer text="Jag behöver 2 st Javautvecklare i Stockholm." />
            
            <AIAnswerContainer text="Jag har identifierat följande roller:\n\n- **2x Javautvecklare** (Stockholm)\n\nStämmer detta?" />
            
            <UserAnswerContainer text="Ja, det stämmer." />
            
            <StepTransitionNotice 
              fromStep={1}
              fromStepTitle="Behovsinsamling"
              toStep={2}
              toStepTitle="Bedöm Kompetensnivå"
            />
            
            <AIAnswerContainer text="Nu ska vi bedöma kompetensnivå för dina resurser. Vilken erfarenhetsnivå behöver du för **Javautvecklare**?" />
          </div>
        </section>
      </div>
    </div>
  );
};

export default ChatDoc;
