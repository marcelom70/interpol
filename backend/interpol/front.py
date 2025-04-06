import streamlit as st

IMAGE_PATH = "./digitalizacao/interpol-london.png"

try:
    with open(IMAGE_PATH, "rb") as img_file:
        img_data = img_file.read()
        st.image(img_data, caption="Mapa Interpol", use_container_width=True)
except FileNotFoundError:
    st.error("Erro: Imagem não encontrada. Verifique o caminho do arquivo!")

html_code = f"""
    <style>
        .container {{
            width: 800px; 
            height: 600px;
            overflow: hidden;
            border: 2px solid #000;
            position: relative;
            margin: auto;
        }}

        .zoom {{
            width: 100%;
            height: 100%;
            transform-origin: center;
            cursor: grab;
            position: absolute;
        }}
    </style>

    <div class="container">
        <img src="{IMAGE_PATH}" class="zoom" id="board" />
    </div>

    <script>
        var img = document.getElementById("board");
        var scale = 1;
        var posX = 0, posY = 0;
        var dragging = false;
        var startX, startY;

        img.addEventListener("wheel", function(event) {{
            event.preventDefault();
            var scaleAmount = event.deltaY * -0.002;
            scale += scaleAmount;
            scale = Math.min(Math.max(0.5, scale), 3);
            img.style.transform = "scale(" + scale + ") translate(" + posX + "px, " + posY + "px)";
        }});

        img.addEventListener("mousedown", function(event) {{
            dragging = true;
            startX = event.clientX - posX;
            startY = event.clientY - posY;
            img.style.cursor = "grabbing";
        }});

        window.addEventListener("mousemove", function(event) {{
            if (dragging) {{
                posX = event.clientX - startX;
                posY = event.clientY - startY;
                img.style.transform = "scale(" + scale + ") translate(" + posX + "px, " + posY + "px)";
            }}
        }});

        window.addEventListener("mouseup", function() {{
            dragging = false;
            img.style.cursor = "grab";
        }});
    </script>
"""

st.components.v1.html(html_code, height=650)
