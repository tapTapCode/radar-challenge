import { useEffect, useMemo, useRef, useState } from 'react'
import L from 'leaflet'
import { Box, Paper, Typography, IconButton, Drawer, Slider, Switch, FormControlLabel, Snackbar, Alert, useMediaQuery } from '@mui/material'
import RefreshIcon from '@mui/icons-material/Refresh'
import SettingsIcon from '@mui/icons-material/Settings'
import { useTheme } from '@mui/material/styles'

export function App() {
  const mapRef = useRef<L.Map | null>(null)
  const [timestamp, setTimestamp] = useState<string | null>(null)
  const theme = useTheme()
  const isDesktop = useMediaQuery(theme.breakpoints.up('md'))
  const [settingsOpen, setSettingsOpen] = useState(false)
  const [gridEnabled, setGridEnabled] = useState(false)
  const [radarOpacity, setRadarOpacity] = useState(0.75)
  const [snackbarOpen, setSnackbarOpen] = useState(false)
  const [snackbarMsg, setSnackbarMsg] = useState('')
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    const map = L.map('map', { zoomControl: true }).setView([39.5, -98.35], 4)
    mapRef.current = map

    const radarLayer = L.tileLayer('/api/tiles/{z}/{x}/{y}.png', {
      opacity: radarOpacity,
      tileSize: 256,
      detectRetina: false
    })
    radarLayer.addTo(map)
    ;(map as any)._radarLayer = radarLayer

    // geographic grid overlay (meridians/parallels) self-hosted, 5° spacing with labels
    const gridLayer = L.gridLayer({ tileSize: 256 })
    ;(gridLayer as any).createTile = function(coords: any) {
      const tile = document.createElement('canvas')
      tile.width = 256; tile.height = 256
      const ctx = tile.getContext('2d')!
      const map = (this as any)._map
      const crs = map.options.crs
      const z = coords.z
      const originX = coords.x * 256
      const originY = coords.y * 256

      const tile2lon = (x: number, z: number) => x / Math.pow(2, z) * 360 - 180
      const tile2lat = (y: number, z: number) => {
        const n = Math.PI - 2 * Math.PI * y / Math.pow(2, z)
        return (180 / Math.PI) * Math.atan(0.5 * (Math.exp(n) - Math.exp(-n)))
      }

      const lonLeft = tile2lon(coords.x, z)
      const lonRight = tile2lon(coords.x + 1, z)
      const latTop = tile2lat(coords.y, z)
      const latBottom = tile2lat(coords.y + 1, z)

      ctx.strokeStyle = 'rgba(255,255,255,0.18)'
      ctx.lineWidth = 1
      ctx.font = '10px system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif'
      ctx.fillStyle = 'rgba(255,255,255,0.9)'

      const step = 5

      // draw meridians every 5° with labels at top edge
      const lonStart = Math.ceil(lonLeft / step) * step
      for (let lon = lonStart; lon < lonRight; lon += step) {
        const top = crs.latLngToPoint(L.latLng(latTop, lon), z)
        const bottom = crs.latLngToPoint(L.latLng(latBottom, lon), z)
        ctx.beginPath()
        ctx.moveTo(top.x - originX, top.y - originY)
        ctx.lineTo(bottom.x - originX, bottom.y - originY)
        ctx.stroke()

        // label near top
        const label = `${lon}°`
        const tx = Math.round(top.x - originX + 3)
        const ty = Math.round(top.y - originY + 12)
        // draw subtle background for readability
        const metrics = ctx.measureText(label)
        const w = Math.ceil(metrics.width) + 4
        ctx.fillStyle = 'rgba(0,0,0,0.35)'
        ctx.fillRect(tx - 2, ty - 9, w, 11)
        ctx.fillStyle = 'rgba(255,255,255,0.9)'
        ctx.fillText(label, tx, ty)
      }

      // draw parallels every 5° with labels at right edge
      const latStart = Math.ceil(latBottom / step) * step
      for (let lat = latStart; lat < latTop; lat += step) {
        const left = crs.latLngToPoint(L.latLng(lat, lonLeft), z)
        const right = crs.latLngToPoint(L.latLng(lat, lonRight), z)
        ctx.beginPath()
        ctx.moveTo(left.x - originX, left.y - originY)
        ctx.lineTo(right.x - originX, right.y - originY)
        ctx.stroke()

        // label near right
        const label = `${lat}°`
        const tx = Math.round(right.x - originX - 4)
        const ty = Math.round(right.y - originY - 4)
        const metrics = ctx.measureText(label)
        const w = Math.ceil(metrics.width) + 4
        ctx.fillStyle = 'rgba(0,0,0,0.35)'
        ctx.fillRect(tx - w, ty - 9, w, 11)
        ctx.fillStyle = 'rgba(255,255,255,0.9)'
        ctx.fillText(label, tx - w + 2, ty)
      }

      return tile
    }
    ;(map as any)._gridLayer = gridLayer
    if (gridEnabled) gridLayer.addTo(map)

    return () => {
      map.remove()
    }
  }, [])

  useEffect(() => {
    const id = setInterval(async () => {
      try {
        const res = await fetch('/api/latest')
        if (res.ok) {
          const data = await res.json()
          setTimestamp(data.timestamp)
          // Bust tile cache by updating tile URL with timestamp query
          const map = mapRef.current as any
          if (map && map._radarLayer && data.timestamp) {
            const base = '/api/tiles/{z}/{x}/{y}.png'
            map._radarLayer.setUrl(`${base}?t=${encodeURIComponent(data.timestamp)}`)
          }
        }
      } catch (e) {
        setSnackbarMsg('Failed to fetch latest timestamp')
        setSnackbarOpen(true)
      }
    }, 60_000)

    // initial fetch
    ;(async () => {
      try {
        const res = await fetch('/api/latest')
        if (res.ok) {
          const data = await res.json()
          setTimestamp(data.timestamp)
          const map = mapRef.current as any
          if (map && map._radarLayer && data.timestamp) {
            const base = '/api/tiles/{z}/{x}/{y}.png'
            map._radarLayer.setUrl(`${base}?t=${encodeURIComponent(data.timestamp)}`)
          }
        }
      } catch (e) {
        setSnackbarMsg('Failed to fetch latest timestamp')
        setSnackbarOpen(true)
      }
    })()

    return () => clearInterval(id)
  }, [])

  const header = useMemo(() => {
    return (
      <Paper elevation={isDesktop ? 8 : 6} sx={{ position: 'absolute', top: 12, left: 12, p: 1.5, borderRadius: 2, bgcolor: 'rgba(0,0,0,0.6)' }}>
        <Box display="flex" alignItems="center" gap={1.5}>
          <Typography variant="h6" fontWeight={700}>MRMS RALA</Typography>
          <Box flexGrow={1} />
          <IconButton size="small" color="default" onClick={() => setSettingsOpen(true)}>
            <SettingsIcon fontSize="small" />
          </IconButton>
          <IconButton size="small" color="primary" disabled={refreshing} onClick={async () => {
            setRefreshing(true)
            try {
              const res = await fetch('/api/latest')
              if (res.ok) {
                const data = await res.json()
                setTimestamp(data.timestamp)
                const map = mapRef.current as any
                if (map && map._radarLayer && data.timestamp) {
                  const base = '/api/tiles/{z}/{x}/{y}.png'
                  map._radarLayer.setUrl(`${base}?t=${encodeURIComponent(data.timestamp)}`)
                }
              } else {
                setSnackbarMsg('Failed to fetch latest timestamp')
                setSnackbarOpen(true)
              }
            } catch (e) {
              setSnackbarMsg('Manual refresh failed')
              setSnackbarOpen(true)
            } finally {
              setRefreshing(false)
            }
          }}>
            <RefreshIcon fontSize="small" sx={{ animation: refreshing ? 'spin 1s linear infinite' : 'none', '@keyframes spin': { '0%': { transform: 'rotate(0deg)' }, '100%': { transform: 'rotate(360deg)' } } }} />
          </IconButton>
        </Box>
        <Typography variant="caption" color="#ddd">
          {timestamp ? `Latest: ${new Date(timestamp).toLocaleString()}` : 'Fetching latest scan…'}
        </Typography>
      </Paper>
    )
  }, [timestamp])

  return (
    <>
      <div id="map" className="map" />
      {header}
      <Paper elevation={isDesktop ? 6 : 3} sx={{ position: 'absolute', right: 12, bottom: 12, p: 1.5, borderRadius: 2, bgcolor: 'rgba(255,255,255,0.92)', color: '#111' }}>
        <Typography variant="subtitle2" fontWeight={700} gutterBottom>Reflectivity (dBZ)</Typography>
        <Box display="flex" alignItems="center" gap={1}>
          {['#6464ff','#00ccff','#00ffcc','#00ff00','#aaff00','#ffee00','#ffcc00','#ff9900','#ff6600','#ff0000','#cc0000','#990000'].map((c,i)=> (
            <Box key={i} sx={{ width: 16, height: 12, borderRadius: 0.5, bgcolor: c }} />
          ))}
        </Box>
        <Box display="flex" justifyContent="space-between" mt={0.5}>
          {['-10','0','10','20','30','40','50','60+'].map((t,i)=> (
            <Typography key={i} variant="caption" color="#333">{t}</Typography>
          ))}
        </Box>
      </Paper>

      <Drawer anchor="right" open={settingsOpen} onClose={() => setSettingsOpen(false)}>
        <Box sx={{ width: 300, p: 2 }}>
          <Typography variant="subtitle1" fontWeight={700} gutterBottom>Settings</Typography>
          <Box mt={2}>
            <Typography variant="caption" gutterBottom>Radar Opacity</Typography>
            <Slider value={radarOpacity} min={0.2} max={1} step={0.05} onChange={(_, v) => {
              const value = Array.isArray(v) ? v[0] as number : v as number
              setRadarOpacity(value)
              const map = mapRef.current as any
              if (map && map._radarLayer) map._radarLayer.setOpacity(value)
            }} />
          </Box>
          <Box mt={1}>
            <FormControlLabel control={<Switch checked={gridEnabled} onChange={(e) => {
              const enabled = e.target.checked
              setGridEnabled(enabled)
              const map = mapRef.current as any
              if (map && map._gridLayer) {
                if (enabled) map._gridLayer.addTo(map)
                else map.removeLayer(map._gridLayer)
              }
            }} />} label="Show grid overlay" />
          </Box>
        </Box>
      </Drawer>

      <Snackbar open={snackbarOpen} autoHideDuration={3000} onClose={() => setSnackbarOpen(false)}>
        <Alert onClose={() => setSnackbarOpen(false)} severity="warning" sx={{ width: '100%' }}>
          {snackbarMsg}
        </Alert>
      </Snackbar>
    </>
  )
}

