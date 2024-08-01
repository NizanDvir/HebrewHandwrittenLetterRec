<script setup>
import { ref } from "vue";
import PaintCanvas from "./components/PaintCanvas.vue";
import VueDrawingCanvas from "vue-drawing-canvas";

const vueCanvasDrawing = ref(null);
const mousePosition = ref({ x: 0, y: 0 });
const brushSettings = ref({
  size: 70,
  tool: "pen",
});
const correct = ref(0);
const total = ref(0);
const labels = ref([]);

document.addEventListener("mousemove", (event) => {
  mousePosition.value.x = event.clientX;
  mousePosition.value.y = event.clientY;
});


const getOptionsPromise = () => {
  return fetch("/api/options")
    .then((response) => response.json())
    .then((data) => {
      return data;
    })
    .catch((error) => {
      console.error("Error:", error);
    });
};

const options = ref({
  targetWidth: 480,
  targetHeight: 480,
  pixelsPerCell: 12,
});

const optionsPromise = getOptionsPromise();
optionsPromise.then((data) => {
  if (!data) {
    console.error("No data received");
    return;
  }
  options.value = {
    width: data.width,
    height: data.height,
    pixelsPerCell: data.pixelsPerCell,
    targetWidth: options.value.targetWidth,
    targetHeight: options.value.targetHeight,
  };
});

const wheel = (event) => {
  if (event.deltaY < 0) {
    brushSettings.value.size = Math.min(5, brushSettings.value.size + 1);
  } else {
    brushSettings.value.size = Math.max(1, brushSettings.value.size - 1);
  }
  if (brushSettings.value.tool === "eraser") {
    return;
  }

  // show border around mouse for 2 seconds the size of the brush
  // if there is already a border, remove it
  const mouse = document.getElementById("mouse");
  if (mouse) {
    mouse.remove();
  }

  const div = document.createElement("div");
  div.id = "mouse";
  div.style.position = "absolute";
  // make it pass through mouse events
  div.style.pointerEvents = "none";
  div.style.border = `${brushSettings.value.size * options.pixelsPerCell}px solid black`;
  div.style.borderRadius = "50%";
  div.style.width = "0px";
  div.style.height = "0px";
  // center of cursor
  div.style.left = `${event.clientX - brushSettings.value.size * options.pixelsPerCell}px`;
  div.style.top = `${event.clientY - brushSettings.value.size * options.pixelsPerCell}px`;
  document.body.appendChild(div);

  document.addEventListener("mousemove", (event) => {
    div.style.left = `${event.clientX - brushSettings.value.size * options.pixelsPerCell}px`;
    div.style.top = `${event.clientY - brushSettings.value.size * options.pixelsPerCell}px`;
  });
  document.addEventListener("mousedown", () => {
    div.remove();
  });

  setTimeout(() => {
    div.remove();
  }, options.pixelsPerCell00);
};

const keypress = (event) => {
  if (event.key === "Z" && (event.ctrlKey || event.metaKey)) {
    vueCanvasDrawing.value.undo();
  } else if (((event.key === "Z") && (event.ctrlKey || event.metaKey)) || (event.shiftKey && event.ctrlKey && event.key === 'Z')) {
    vueCanvasDrawing.value.redo();
  }
};

const saveImageAndSendToServer = () => {
  fetch("http://localhost:5000/save", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      dataURL: vueCanvasDrawing.value.save(),
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Success:", data);
      // sort by label
      // convert to array of objects: {letter: X, prediction: Y}
      // sort by prediction

      const sorted = Object.entries(data.kwargs.labels).sort((a, b) => b[1] - a[1]);
      labels.value = sorted;

      // calcAcc(label);
    })
    .catch((error) => {
      console.error("Error:", error);
    });
};

function calcAcc(label) {
  let letter = getLetter(label);
  if (confirm("Is this your letter?" + letter)) {
    correct.value++;
  }
  total.value++;
}

function getLetter(label) {
  // define dict to turn label to letter
  const dict = {
    0: "א",
    1: "ב",
    2: "ג",
    3: "ד",
    4: "ה",
    5: "ו",
    6: "ז",
    7: "ח",
    8: "ט",
    9: "י",
    10: "כ",
    11: "ך",
    12: "ל",
    13: "מ",
    14: "ם",
    15: "נ",
    16: "ן",
    17: "ס",
    18: "ע",
    19: "פ",
    20: "ף",
    21: "צ",
    22: "ץ",
    23: "ק",
    24: "ר",
    25: "ש",
    26: "ת",
  };

  let letter = dict[label];
  return letter;
}
</script>

<template>
  <div @wheel="wheel" @keypress="keypress" class="flex flex-col h-svh items-center justify-center gap-32">
    <!-- hollow Border that follows mouse -->
    <div v-if="brushSettings.tool === 'eraser'" class="overflow-hidden" :style="{
    position: 'absolute',
    pointerEvents: 'none',
    border: '2px solid black',
    borderRadius: '50%',
    width: `${brushSettings.size * options.pixelsPerCell}px`,
    height: `${brushSettings.size * options.pixelsPerCell}px`,
    left: `${mousePosition.x - brushSettings.size * 10}px`,
    top: `${mousePosition.y - brushSettings.size * 10}px`,
  }">
    </div>

    <div class="flex flex-col gap-2 justify-center items-center">
      <div class="flex justify-center" @click="saveImageAndSendToServer">
        <button class="border border-black rounded-md p-5 w-32 bg-gray-200">Predict</button>
      </div>
      <div class="flex gap-5 items-center justify-center">
        <div class="flex flex-col items-center justify-center">
          <!-- <PaintCanvas :tool="brushSettings.tool" :pixel-size="options.pixelsPerCell" ref="vueCanvasDrawing" /> -->
          <VueDrawingCanvas class="border-2 border-black" ref="vueCanvasDrawing"
            :line-width="Number(brushSettings.size)" :width="options.targetWidth" :height="options.targetHeight" />
          <p>{{ (correct / (total === 0 ? 1 : total) * 100).toFixed(2) }}%</p>
          <div v-if="labels.length > 0" class="flex gap-4 mt-2">
            <button
              @click="() => { correct++; total++; console.log('correct:', correct, 'total:', total); vueCanvasDrawing.reset(); labels = [] }"
              class="bg-green-500 p-2 rounded-[10px] w-10 h-10 flex items-center justify-center">YES</button>
            <button
              @click="() => { total++; console.log('correct:', correct, 'total:', total); vueCanvasDrawing.reset(); labels = [] }"
              class="bg-red-500 rounded-[10px] w-10 h-10 flex items-center justify-center">NO</button>
          </div>
        </div>
        <div class="grid grid-cols-3 gap-4 h-full">
          <div v-for="(label, index) in labels" :key="label"
            class="rounded-[10px] text-center flex justify-center items-center p-2 border border-black"
            :class="index === 0 ? 'col-span-3 h-20 text-2xl bg-gray-400' : 'bg-gray-200'">
            {{ getLetter(label[0]) }}: {{ (label[1] * 100).toFixed(2) }}%
          </div>
        </div>
      </div>
    </div>
    <div>
      <div class="flex gap-5 p-2">
        <button class="border border-black rounded-md p-2" @click="vueCanvasDrawing.undo()">Undo</button>
        <button class="border border-black rounded-md p-2" @click="vueCanvasDrawing.redo()">Redo</button>
        <button class="border border-black rounded-md p-2" @click="vueCanvasDrawing.reset()">Clear</button>
      </div>
      <div class="flex gap-5">
        <!-- Eraser -->
        <div class="flex flex-col">
          <input type="radio" id="pen" name="tool" value="pen" v-model="brushSettings.tool" />
          <label for="pen">Pen</label>
        </div>
        <div class="flex flex-col">
          <input type="radio" id="eraser" name="tool" value="eraser" v-model="brushSettings.tool" />
          <label for="eraser">Eraser</label>
        </div>
      </div>
      <div>
        <!-- slider for brushSize -->
        <input type="range" min="40" max="80" v-model="brushSettings.size" />
      </div>
    </div>
  </div>
</template>