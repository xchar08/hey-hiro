import { Tooltip } from '@chakra-ui/react'
import { ReactNode } from 'react'
export default function TutorialTooltip({ content, children, placement='top' }: { content:string, children:ReactNode, placement?:any }) {
  return <Tooltip label={content} hasArrow placement={placement}>{children}</Tooltip>
}