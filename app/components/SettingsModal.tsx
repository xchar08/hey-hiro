import { Modal, ModalOverlay, ModalContent, ModalHeader, ModalCloseButton,
    ModalBody, ModalFooter, Button, FormControl, FormLabel, Input, Slider,
    SliderTrack, SliderFilledTrack, SliderThumb, Select } from '@chakra-ui/react'
  import { useState, useEffect } from 'react'
  
  export default function SettingsModal({ isOpen, onClose,
    auraColor, setAuraColor, voiceSpeed, setVoiceSpeed,
    theme, setTheme, cerebrasKey, setCerebrasKey
  }: any) {
    const [localColor,setLocalColor]=useState(auraColor)
    const [localSpeed,setLocalSpeed]=useState(voiceSpeed)
    const [localTheme,setLocalTheme]=useState(theme)
    const [localKey,setLocalKey]=useState(cerebrasKey)
    useEffect(()=>{ if(isOpen){ setLocalColor(auraColor); setLocalSpeed(voiceSpeed); setLocalTheme(theme); setLocalKey(cerebrasKey) }},[isOpen])
    const handleSave=()=>{
      setAuraColor(localColor)
      setVoiceSpeed(localSpeed)
      setTheme(localTheme)
      setCerebrasKey(localKey)
      localStorage.setItem('cerebrasKey',localKey)
      onClose()
    }
    return (
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Settings</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FormControl mb={4}><FormLabel>Aura Color</FormLabel>
              <Input type="color" value={localColor} onChange={e=>setLocalColor(e.target.value)}/>
            </FormControl>
            <FormControl mb={4}><FormLabel>Voice Speed ({localSpeed.toFixed(1)}x)</FormLabel>
              <Slider min={0.5} max={2} step={0.1} value={localSpeed} onChange={setLocalSpeed}>
                <SliderTrack><SliderFilledTrack/></SliderTrack>
                <SliderThumb/>
              </Slider>
            </FormControl>
            <FormControl mb={4}><FormLabel>Theme</FormLabel>
              <Select value={localTheme} onChange={e=>setLocalTheme(e.target.value)}>
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </Select>
            </FormControl>
            <FormControl mb={4}><FormLabel>Cerebras API Key</FormLabel>
              <Input value={localKey} onChange={e=>setLocalKey(e.target.value)} placeholder="Enter key"/>
            </FormControl>
          </ModalBody>
          <ModalFooter>
            <Button colorScheme="blue" mr={3} onClick={handleSave}>Save</Button>
            <Button variant="ghost" onClick={onClose}>Cancel</Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    )
  }