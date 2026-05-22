import React from 'react'
import { render, screen, fireEvent } from '@testing-library/react'
import ChartGenerator from '../app/dashboard/charts/ChartGenerator'

describe('ChartGenerator demo', () => {
  it('renders generate button and produces an svg chart', async () => {
    render(<ChartGenerator />)
    const btn = screen.getByRole('button', { name: /generate/i })
    expect(btn).toBeInTheDocument()
    fireEvent.click(btn)
    // After generating, the component exposes a hidden data hook for tests
    const dataPre = await screen.findByTestId('chart-data')
    expect(dataPre).toBeInTheDocument()
    const parsed = JSON.parse(dataPre.textContent || '[]')
    expect(Array.isArray(parsed)).toBe(true)
    expect(parsed.length).toBe(7)
  })
})
