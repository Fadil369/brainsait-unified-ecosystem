import {
    AttachFile,
    Clear,
    Mic,
    Psychology,
    Send,
    SmartToy,
} from '@mui/icons-material';
import {
    Box,
    Button,
    Card,
    CardContent,
    Chip,
    IconButton,
    Paper,
    TextField,
    Typography,
} from '@mui/material';
import { useState } from 'react';
import { useLanguage } from '../hooks/useLanguage';

const ChatAssistant = () => {
  const { isRTL } = useLanguage();
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([
    {
      id: 1,
      type: 'assistant',
      content: isRTL 
        ? 'مرحباً! أنا مساعد الذكاء الاصطناعي للرعاية الصحية. كيف يمكنني مساعدتك اليوم؟'
        : 'Hello! I am your AI healthcare assistant. How can I help you today?',
      timestamp: new Date()
    }
  ]);
  const [isTyping, setIsTyping] = useState(false);

  const handleSendMessage = () => {
    if (!message.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date()
    };

    setChatHistory(prev => [...prev, userMessage]);
    setMessage('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const aiResponse = {
        id: Date.now() + 1,
        type: 'assistant',
        content: isRTL 
          ? 'شكراً لك على رسالتك. أنا أعمل على تحليل استفسارك وسأقدم لك الإجابة المناسبة قريباً.'
          : 'Thank you for your message. I am analyzing your query and will provide an appropriate response soon.',
        timestamp: new Date()
      };
      setChatHistory(prev => [...prev, aiResponse]);
      setIsTyping(false);
    }, 2000);
  };

  const clearChat = () => {
    setChatHistory([{
      id: 1,
      type: 'assistant',
      content: isRTL 
        ? 'مرحباً! أنا مساعد الذكاء الاصطناعي للرعاية الصحية. كيف يمكنني مساعدتك اليوم؟'
        : 'Hello! I am your AI healthcare assistant. How can I help you today?',
      timestamp: new Date()
    }]);
  };

  const quickQuestions = [
    isRTL ? 'كيف أقدم مطالبة نفيس؟' : 'How to submit NPHIES claim?',
    isRTL ? 'ما هي معايير FHIR؟' : 'What are FHIR standards?',
    isRTL ? 'كيف أدير بيانات المرضى؟' : 'How to manage patient data?',
    isRTL ? 'شرح نظام OID' : 'Explain OID system'
  ];

  return (
    <Box sx={{ height: '80vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center" gap={2}>
            <SmartToy sx={{ color: 'primary.main', fontSize: 32 }} />
            <Box>
              <Typography variant="h6">
                {isRTL ? 'مساعد الذكاء الاصطناعي الطبي' : 'Medical AI Assistant'}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {isRTL ? 'متاح 24/7 لمساعدتك' : 'Available 24/7 to help you'}
              </Typography>
            </Box>
          </Box>
          <Button
            variant="outlined"
            startIcon={<Clear />}
            onClick={clearChat}
            size="small"
          >
            {isRTL ? 'مسح المحادثة' : 'Clear Chat'}
          </Button>
        </Box>
      </Paper>

      {/* Quick Questions */}
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          {isRTL ? 'أسئلة سريعة:' : 'Quick Questions:'}
        </Typography>
        <Box display="flex" gap={1} flexWrap="wrap">
          {quickQuestions.map((question, index) => (
            <Chip
              key={index}
              label={question}
              variant="outlined"
              clickable
              onClick={() => setMessage(question)}
              size="small"
            />
          ))}
        </Box>
      </Paper>

      {/* Chat Area */}
      <Paper sx={{ flexGrow: 1, p: 2, overflow: 'auto', mb: 2 }}>
        <Box display="flex" flexDirection="column" gap={2}>
          {chatHistory.map((msg) => (
            <Box
              key={msg.id}
              display="flex"
              justifyContent={msg.type === 'user' ? 'flex-end' : 'flex-start'}
            >
              <Card
                sx={{
                  maxWidth: '70%',
                  bgcolor: msg.type === 'user' ? 'primary.main' : 'background.paper',
                  color: msg.type === 'user' ? 'primary.contrastText' : 'text.primary'
                }}
              >
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Box display="flex" alignItems="flex-start" gap={1}>
                    {msg.type === 'assistant' && (
                      <Psychology sx={{ color: 'secondary.main', mt: 0.5 }} />
                    )}
                    <Box>
                      <Typography variant="body2">
                        {msg.content}
                      </Typography>
                      <Typography variant="caption" sx={{ opacity: 0.7, mt: 1, display: 'block' }}>
                        {msg.timestamp.toLocaleTimeString()}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Box>
          ))}
          
          {isTyping && (
            <Box display="flex" justifyContent="flex-start">
              <Card sx={{ bgcolor: 'background.paper' }}>
                <CardContent sx={{ p: 2 }}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Psychology sx={{ color: 'secondary.main' }} />
                    <Typography variant="body2">
                      {isRTL ? 'يكتب...' : 'Typing...'}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Box>
          )}
        </Box>
      </Paper>

      {/* Input Area */}
      <Paper sx={{ p: 2 }}>
        <Box display="flex" gap={1} alignItems="flex-end">
          <TextField
            fullWidth
            multiline
            maxRows={3}
            placeholder={isRTL ? 'اكتب رسالتك هنا...' : 'Type your message here...'}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
          />
          <IconButton color="primary">
            <AttachFile />
          </IconButton>
          <IconButton color="primary">
            <Mic />
          </IconButton>
          <Button
            variant="contained"
            onClick={handleSendMessage}
            disabled={!message.trim() || isTyping}
            sx={{ minWidth: 'auto', px: 2 }}
          >
            <Send />
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default ChatAssistant;
