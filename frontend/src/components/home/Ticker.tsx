import { tickerItems } from '../../data/content'

export function Ticker() {
  return (
    <div className="ticker" aria-hidden="true">
      <div className="ticker-track">
        {[...tickerItems, ...tickerItems].map((item, index) => (
          <span className="ticker-item" key={`${item}-${index}`}>
            {item}
          </span>
        ))}
      </div>
    </div>
  )
}
