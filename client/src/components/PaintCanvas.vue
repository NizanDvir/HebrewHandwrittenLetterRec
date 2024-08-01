<template>
  <div>
    <canvas ref="canvas" @mousedown="startDrawing" @mousemove="draw" @mouseup="stopDrawing"
      @mouseleave="stopDrawing"></canvas>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted } from 'vue';

export default defineComponent({
  name: 'PixelArtComponent',
  props: {
    pixelSize: {
      type: Number,
      default: 40,
    },
    tool: {
      type: String,
      default: 'pen', // other possible value: 'eraser'
    },
  },
  setup(props) {
    const canvas = ref(null);
    const ctx = ref(null);
    const drawing = ref(false);
    const currentColor = ref('black');

    const undoStack = ref([]);
    const redoStack = ref([]);

    const setColor = (color) => {
      currentColor.value = color;
    };

    const saveState = () => {
      if (undoStack.value.length >= 10) {
        undoStack.value.shift(); // Keep only the last 10 states
      }
      undoStack.value.push(canvas.value.toDataURL());
    };

    const restoreState = (stack) => {
      if (stack.length > 0) {
        const state = stack.pop();
        const img = new Image();
        img.src = state;
        img.onload = () => {
          ctx.value.clearRect(0, 0, canvas.value.width, canvas.value.height);
          ctx.value.drawImage(img, 0, 0);
        };
      }
    };

    const undo = () => {
      if (undoStack.value.length > 0) {
        redoStack.value.push(canvas.value.toDataURL());
        restoreState(undoStack.value);
      }
    };

    const redo = () => {
      if (redoStack.value.length > 0) {
        undoStack.value.push(canvas.value.toDataURL());
        restoreState(redoStack.value);
      }
    };

    const startDrawing = (event) => {
      saveState();
      drawing.value = true;
      draw(event);
    };

    const draw = (event) => {
      if (!drawing.value) return;
      const rect = canvas.value.getBoundingClientRect();
      const x = Math.floor((event.clientX - rect.left) / props.pixelSize) * props.pixelSize;
      const y = Math.floor((event.clientY - rect.top) / props.pixelSize) * props.pixelSize;

      if (props.tool === 'pen') {
        ctx.value.fillStyle = currentColor.value;
        ctx.value.fillRect(x, y, props.pixelSize, props.pixelSize);
      } else if (props.tool === 'eraser') {
        ctx.value.clearRect(x, y, props.pixelSize, props.pixelSize);
      }
    };

    const stopDrawing = () => {
      drawing.value = false;
    };

    const clearCanvas = () => {
      saveState();
      ctx.value.clearRect(0, 0, canvas.value.width, canvas.value.height);
    };

    onMounted(() => {
      ctx.value = canvas.value.getContext('2d');
      canvas.value.width = 480;
      canvas.value.height = 480;
      ctx.value.imageSmoothingEnabled = false;
    });

    return { canvas, setColor, startDrawing, draw, stopDrawing, clearCanvas, undo, redo };
  },
});
</script>

<style scoped>
canvas {
  border: 1px solid black;
}
</style>
