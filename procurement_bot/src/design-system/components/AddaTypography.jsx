import React from 'react';
import { tokens } from '../tokens';

const headingBase = {
  fontFamily: tokens.typography.fontFamily,
  color: tokens.colors.neutral.text,
  margin: 0,
  marginBottom: tokens.spacing.xl,
};

export const H1 = ({ children, className = '', style = {}, color }) => (
  <h1 style={{
    ...headingBase,
    fontSize: tokens.typography.sizes['4xl'],
    fontWeight: tokens.typography.weights.bold,
    lineHeight: tokens.typography.lineHeights.tight,
    color: color || tokens.colors.brand.primary, // Default H1 is often Brand Primary in Hero
    ...style
  }} className={className}>
    {children}
  </h1>
);

export const H2 = ({ children, className = '', style = {}, color }) => (
  <h2 style={{
    ...headingBase,
    fontSize: tokens.typography.sizes['2xl'],
    fontWeight: tokens.typography.weights.bold,
    lineHeight: tokens.typography.lineHeights.normal,
    color: color || tokens.colors.neutral.text,
    ...style
  }} className={className}>
    {children}
  </h2>
);

export const H3 = ({ children, className = '', style = {}, color }) => (
  <h3 style={{
    ...headingBase,
    fontSize: tokens.typography.sizes.xl,
    fontWeight: tokens.typography.weights.semibold,
    lineHeight: tokens.typography.lineHeights.normal,
    color: color || tokens.colors.neutral.text,
    ...style
  }} className={className}>
    {children}
  </h3>
);

export const H4 = ({ children, className = '', style = {}, color }) => (
  <h4 style={{
    ...headingBase,
    fontSize: tokens.typography.sizes.lg,
    fontWeight: tokens.typography.weights.semibold,
    lineHeight: tokens.typography.lineHeights.normal,
    color: color || tokens.colors.neutral.text,
    ...style
  }} className={className}>
    {children}
  </h4>
);

export const BodyText = ({ children, className = '', style = {}, size = 'base', bold = false, color }) => (
  <p style={{
    fontFamily: tokens.typography.fontFamily,
    fontSize: tokens.typography.sizes[size],
    fontWeight: bold ? tokens.typography.weights.bold : tokens.typography.weights.regular,
    lineHeight: tokens.typography.lineHeights.relaxed,
    color: color || tokens.colors.neutral.text,
    marginBottom: tokens.spacing.lg,
    ...style
  }} className={className}>
    {children}
  </p>
);

export const Caption = ({ children, className = '', style = {}, color }) => (
  <span style={{
    fontFamily: tokens.typography.fontFamily,
    fontSize: tokens.typography.sizes.sm,
    fontWeight: tokens.typography.weights.regular,
    lineHeight: tokens.typography.lineHeights.normal,
    color: color || tokens.colors.neutral.lightGrey,
    ...style
  }} className={className}>
    {children}
  </span>
);
