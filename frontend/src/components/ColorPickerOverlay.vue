<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { useAppState } from '../composables/useAppState'

const { showColorPicker, originalProjectColor, activeProject, saveProjectColor } = useAppState()

// High-definition internal resolution for the buffer
const INTERNAL_RES = 512
const RADIUS = INTERNAL_RES / 2
const INNER_RADIUS = 100
const OUTER_RADIUS = 250
const RING_WIDTH = OUTER_RADIUS - INNER_RADIUS

// Refs
const canvasRef = ref(null)
const overlayRef = ref(null)
const hexInput = ref(activeProject.color)
let ctx = null
let wheelCache = null

/**
 * Generates a high-fidelity HSL wheel pixel-by-pixel.
 * This is the only method guaranteed to provide zero-gap rendering and
 * perfect black/white zones across all WebView versions.
 */
const createStaticWheel = () => {
    const c = document.createElement('canvas')
    c.width = INTERNAL_RES
    c.height = INTERNAL_RES
    const tempCtx = c.getContext('2d')
    const imageData = tempCtx.createImageData(INTERNAL_RES, INTERNAL_RES)
    const data = imageData.data

    for (let y = 0; y < INTERNAL_RES; y++) {
        for (let x = 0; x < INTERNAL_RES; x++) {
            const dx = x - RADIUS
            const dy = y - RADIUS
            const dist = Math.sqrt(dx * dx + dy * dy)
            const index = (y * INTERNAL_RES + x) * 4

            // Alpha masking for the ring shape with antialiasing
            let alpha = 0
            if (dist >= INNER_RADIUS - 1 && dist <= OUTER_RADIUS + 1) {
                if (dist < INNER_RADIUS) alpha = dist - (INNER_RADIUS - 1)
                else if (dist > OUTER_RADIUS) alpha = (OUTER_RADIUS + 1) - dist
                else alpha = 1
            }

            if (alpha <= 0) {
                data[index + 3] = 0
                continue
            }

            // Calculate HSL components
            let angle = Math.atan2(dy, dx) * (180 / Math.PI) + 90
            if (angle < 0) angle += 360

            let pos = (dist - INNER_RADIUS) / RING_WIDTH
            let l = 0.5
            // Inner half: White to Pure color
            if (pos < 0.5) l = 1.0 - pos
            // Outer half: Pure color to Black
            else l = 0.5 - (pos - 0.5)

            const [r, g, b] = hslToRgb(angle / 360, 1.0, l)

            data[index] = r
            data[index + 1] = g
            data[index + 2] = b
            data[index + 3] = Math.floor(alpha * 255)
        }
    }

    tempCtx.putImageData(imageData, 0, 0)
    return c
}

const render = () => {
    if (!ctx || !wheelCache) return
    ctx.clearRect(0, 0, INTERNAL_RES, INTERNAL_RES)

    // Draw the high-fidelity buffer
    ctx.drawImage(wheelCache, 0, 0)

    // Center Preview Circle
    ctx.save()
    ctx.beginPath()
    ctx.arc(RADIUS, RADIUS, INNER_RADIUS + 2, 0, Math.PI * 2)
    ctx.fillStyle = activeProject.color
    ctx.fill()
    ctx.strokeStyle = 'rgba(255,255,255,0.2)'
    ctx.lineWidth = 4
    ctx.stroke()
    ctx.restore()
}

const updateLuminance = (hex) => {
    try {
        const h = hex.replace('#', '')
        const r = parseInt(h.substring(0, 2), 16)
        const g = parseInt(h.substring(2, 4), 16)
        const b = parseInt(h.substring(4, 6), 16)
        const luminance = (0.299 * r + 0.587 * g + 0.114 * b)
        activeProject.fontColor = luminance > 150 ? 'dark' : 'light'
    } catch (e) {}
}

const handleMove = (e) => {
    const rect = canvasRef.value.getBoundingClientRect()
    const scale = INTERNAL_RES / rect.width
    const mx = (e.clientX - rect.left) * scale
    const my = (e.clientY - rect.top) * scale

    const dx = mx - RADIUS
    const dy = my - RADIUS
    const dist = Math.sqrt(dx * dx + dy * dy)

    if (dist >= INNER_RADIUS && dist <= OUTER_RADIUS) {
        let angle = Math.atan2(dy, dx) * (180 / Math.PI) + 90
        if (angle < 0) angle += 360

        let pos = (dist - INNER_RADIUS) / RING_WIDTH
        let l = 0.5
        if (pos < 0.5) l = 1.0 - pos
        else l = 0.5 - (pos - 0.5)

        const [r, g, b] = hslToRgb(angle / 360, 1.0, l)
        const hex = rgbToHex(r, g, b)

        activeProject.color = hex
        hexInput.value = hex
        updateLuminance(hex)
        render()
    }
}

const onManualInput = (e) => {
    let val = e.target.value
    if (!val.startsWith('#')) val = '#' + val
    hexInput.value = val

    if (/^#?([0-9A-F]{3}){1,2}$/i.test(val)) {
        activeProject.color = val
        updateLuminance(val)
        render()
    }
}

const handleConfirm = async () => {
    await saveProjectColor(activeProject.color)
    showColorPicker.value = false
}

const handleCancel = () => {
    activeProject.color = originalProjectColor.value
    updateLuminance(activeProject.color)
    showColorPicker.value = false
}

const onKeyDown = (e) => {
    if (e.key === 'Escape') handleCancel()
    if (e.key === 'Enter') handleConfirm()
}

onMounted(async () => {
    await nextTick()
    ctx = canvasRef.value.getContext('2d')
    wheelCache = createStaticWheel()
    render()
    window.addEventListener('keydown', onKeyDown)
})

onUnmounted(() => {
    window.removeEventListener('keydown', onKeyDown)
})

// --- Math Helpers ---

function hslToRgb(h, s, l) {
    let r, g, b
    if (s === 0) {
        r = g = b = l
    } else {
        const hue2rgb = (p, q, t) => {
            if (t < 0) t += 1
            if (t > 1) t -= 1
            if (t < 1 / 6) return p + (q - p) * 6 * t
            if (t < 1 / 2) return q
            if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6
            return p
        }
        const q = l < 0.5 ? l * (1 + s) : l + s - l * s
        const p = 2 * l - q
        r = hue2rgb(p, q, h + 1 / 3)
        g = hue2rgb(p, q, h)
        b = hue2rgb(p, q, h - 1 / 3)
    }
    return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)]
}

function rgbToHex(r, g, b) {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1)
}
</script>

<template>
    <div
        ref="overlayRef"
        class="absolute inset-0 bg-black/85 backdrop-blur-xl flex items-center justify-center z-[200] animate-in fade-in duration-200 overflow-hidden"
        @click.self="handleCancel"
    >
        <!-- Horizontal Percentual Layout -->
        <div class="w-full h-full max-h-[85%] flex items-center justify-between px-[6vw] animate-in zoom-in-95 duration-300">

            <!-- LEFT: Manual Input Column -->
            <div class="flex-1 flex flex-col items-center justify-center min-w-[120px] max-w-[200px]">
                <div class="flex flex-col items-center space-y-3 w-full">
                    <span class="text-[10px] font-black text-gray-500 uppercase tracking-[0.3em] mb-1">Project Color</span>
                    <input
                        type="text"
                        v-model="hexInput"
                        @input="onManualInput"
                        @keyup.enter="handleConfirm"
                        class="w-full bg-cm-input-bg border-2 border-gray-700 focus:border-cm-blue text-white font-mono text-center text-lg md:text-xl py-3 rounded shadow-inner outline-none transition-colors uppercase"
                        maxlength="7"
                    >
                    <p class="text-[9px] font-bold text-gray-600 uppercase tracking-widest text-center leading-tight">Press ENTER to set</p>
                </div>
            </div>

            <!-- CENTER: The Responsive Wheel -->
            <div class="relative group shrink-0 mx-4">
                <!-- Outer Shadow/Glow -->
                <div
                    class="absolute inset-0 rounded-full blur-3xl opacity-20 transition-colors duration-500"
                    :style="{ backgroundColor: activeProject.color }"
                ></div>

                <canvas
                    ref="canvasRef"
                    :width="INTERNAL_RES"
                    :height="INTERNAL_RES"
                    class="cursor-crosshair drop-shadow-2xl w-[clamp(300px,48vh,540px)] h-[clamp(300px,48vh,540px)]"
                    @mousemove="handleMove"
                    @click="handleConfirm"
                ></canvas>

                <!-- Central Contrast Text -->
                <div
                    class="absolute inset-0 z-20 flex items-center justify-center pointer-events-none transition-colors duration-200"
                    :class="activeProject.fontColor === 'dark' ? 'text-black' : 'text-white'"
                >
                    <div class="flex flex-col items-center space-y-0.5">
                        <span class="text-[9px] font-black uppercase tracking-[0.2em] opacity-80">Pick a</span>
                        <span class="text-sm font-black uppercase tracking-[0.4em]">Color</span>
                    </div>
                </div>
            </div>

            <!-- RIGHT: Cancel Action Column -->
            <div class="flex-1 flex flex-col items-center justify-center min-w-[120px] max-w-[200px]">
                <button
                    @click="handleCancel"
                    class="w-full max-w-[140px] bg-gray-800 hover:bg-gray-700 text-gray-400 hover:text-white border border-gray-700 py-3 md:py-4 rounded font-bold text-[10px] md:text-xs uppercase tracking-[0.2em] shadow-md transition-all active:scale-95"
                >
                    Cancel
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
canvas {
    image-rendering: auto;
}
</style>