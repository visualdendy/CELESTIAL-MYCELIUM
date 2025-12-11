from flask import Flask, render_template_string

app = Flask(__name__)

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CELESTIAL MYCELIUM</title>
<style>
html, body {
    margin: 0;
    padding: 0;
    overflow: hidden;
    background: black;
}
canvas {
    width: 100vw;
    height: 100vh;
    display: block;
}
</style>
</head>
<body>
<canvas id="glcanvas"></canvas>

<script>
const canvas = document.getElementById("glcanvas");
const gl = canvas.getContext("webgl");

canvas.width = innerWidth;
canvas.height = innerHeight;

// ============================
// Vertex Shader
// ============================
const VS = `
attribute vec2 position;
void main(){
    gl_Position = vec4(position, 0.0, 1.0);
}
`;

// ============================
// Fragment Shader (Celestial Mycelium)
// ============================
const FS = `
precision highp float;

uniform vec2 u_res;
uniform float u_time;

// Hash
float hash(vec2 p){
    return fract(sin(dot(p, vec2(27.1, 91.7))) * 43758.5453);
}

// Noise
float noise(vec2 p){
    vec2 i = floor(p);
    vec2 f = fract(p);

    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));

    vec2 u = f*f*(3.0 - 2.0*f);

    return mix(a, b, u.x)
         + (c - a) * u.y * (1.0 - u.x)
         + (d - b) * u.x * u.y;
}

// Fractional Brownian Motion
float fbm(vec2 p){
    float v = 0.0;
    float amp = 0.5;
    for(int i=0; i<5; i++){
        v += amp * noise(p);
        p *= 2.0;
        amp *= 0.5;
    }
    return v;
}

void main(){
    vec2 uv = gl_FragCoord.xy / u_res;
    vec2 p = uv - 0.5;
    p.x *= u_res.x / u_res.y;

    float t = u_time * 0.15;

    vec2 flow = vec2(
        fbm(p * 3.0 + t),
        fbm(p * 3.0 - t)
    );

    float tendril = fbm(p * 8.0 + flow * 2.0);
    tendril = smoothstep(0.55, 0.85, tendril);

    float pulse = 0.3 + 0.2 * sin(u_time * 0.8);

    vec3 color = vec3(0.0);
    color += tendril * vec3(0.6, 0.8, 1.0);
    color += pulse * tendril * vec3(0.3, 0.2, 1.0);
    color += exp(-abs(flow.x) * 4.0) * 0.05;

    gl_FragColor = vec4(color, 1.0);
}
`;

// ============================
// Shader compiler
// ============================
function compile(type, src){
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    return s;
}

const vs = compile(gl.VERTEX_SHADER, VS);
const fs = compile(gl.FRAGMENT_SHADER, FS);

const program = gl.createProgram();
gl.attachShader(program, vs);
gl.attachShader(program, fs);
gl.linkProgram(program);
gl.useProgram(program);

// Full-screen quad
const buffer = gl.createBuffer();
gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
gl.bufferData(
    gl.ARRAY_BUFFER,
    new Float32Array([
        -1,-1, 1,-1, -1,1,
        -1,1, 1,-1, 1,1
    ]),
    gl.STATIC_DRAW
);

const posLoc = gl.getAttribLocation(program, "position");
gl.enableVertexAttribArray(posLoc);
gl.vertexAttribPointer(posLoc, 2, gl.FLOAT, false, 0, 0);

// Uniforms
const uTime = gl.getUniformLocation(program, "u_time");
const uRes  = gl.getUniformLocation(program, "u_res");

function render(time){
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.uniform1f(uTime, time * 0.001);
    gl.uniform2f(uRes, canvas.width, canvas.height);

    gl.drawArrays(gl.TRIANGLES, 0, 6);
    requestAnimationFrame(render);
}
requestAnimationFrame(render);

addEventListener("resize", () => {
    canvas.width = innerWidth;
    canvas.height = innerHeight;
});
</script>

</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
