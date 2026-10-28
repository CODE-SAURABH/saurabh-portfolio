import { Link } from 'react-router-dom'
import type { ReactNode } from 'react'

interface ButtonLinkProps {
  to: string
  children: ReactNode
  variant?: 'primary' | 'secondary'
  size?: 'default' | 'small'
  className?: string
}

export function ButtonLink({
  to,
  children,
  variant = 'secondary',
  size = 'default',
  className = '',
}: ButtonLinkProps) {
  const classes = [
    'button',
    variant === 'primary' ? 'button--primary' : '',
    size === 'small' ? 'button--small' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ')

  return (
    <Link className={classes} to={to}>
      {children}
    </Link>
  )
}
