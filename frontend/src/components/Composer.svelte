<script>
    import { Button, Col, Row } from 'sveltestrap';
    import { onMount } from "svelte";

    let data = {"title": "untitled", "artist": "nobody", "content": ""};
    let scroller = null;
    let scrollPaused = false;

    export let id = null;
    if (id !== null) {
        onMount(async function() {
            const response = await fetch(`http://localhost:8000/songs/${id}`);
            const json = await response.json();
            data = json;
        });
    }

    async function saveSong() {
        const form = document.getElementById('editor-form');
        const formData = new FormData();
        let url = "";
        if (id !== null) {
            url = `http://localhost:8000/songs/${id}`;
        } else {
            url = `http://localhost:8000/songs`;
        }
        formData.append("title", form.title.value);
        formData.append("artist", form.artist.value);
        formData.append("content", form.content.value);
        const response = await fetch(url, {
            method: "post",
            body: formData,
        })
        const json = await response.json();
        let viewerContent= document.getElementById("viewer-content");
        viewerContent.innerHTML = json.parsed_content;
    }

    async function transposeSong() {
        // degree = document.getElementById("degree").value;
        // const form = document.getElementById('editor-form');
        // let content = form.content.value;
    }

    function startScrolling() {
        var topPos = viewer.offsetTop
        stopScrolling()
        scroll(topPos)
    }

    function stopScrolling() {
        clearInterval(scroller)
    }

    function toggleScrolling() {
        scrollPaused = scrollPaused ? false : true
    }

    function scroll(topPos) {
        let viewerContent= document.getElementById("viewer-content");
        viewer.scrollTop = topPos - viewerContent.offsetTop
        scroller = setInterval(function() { 
            if(!scrollPaused) {
                viewer.scrollTop += 4
            }
        }, 500)
    }

    function updateFontSize(op) {
        let viewerContent = document.getElementById("viewer-content");
        var fontSize = parseInt(window.getComputedStyle(viewerContent, null).getPropertyValue('font-size'));
        if (op == "-")
            fontSize -= 5
        else
            fontSize += 5
        viewerContent.style.fontSize = fontSize.toString()+"px"
    }
</script>

<style>

body {
    font-family: monospace;
}

:global(.chord) {
    font-weight: bold;
}

:global(.chord-delimiter) {
    padding: 3px;
}

#viewer {
    font-size: 18px;
    overflow-y: scroll; 
    height: 1000px;
    margin-top: 10px;
}
#editor-form.textarea {
    display: block;
}
#editor-form.input {
    margin-top: 10px;
    margin-bottom: 10px;
    display: block;
}
#editor-form.label {
    margin-bottom: 10px;
}

button {
    display: inline-block;
}
</style>

<h1>Composer</h1>
<div id="editor">
<form id="editor-form">
    title: <input type="text" id="title" value="{data.title}">
    <br>
    artist: <input type="text" id="artist" value="{data.artist}">
    <br>
    content: <textarea rows="50" cols="100" id="content" value="{data.content}"></textarea>
</form>
</div>

<div id="viewer">
    <div id="viewer-content">{@html data.parsed_content}</div>
</div>

<Button color="primary" on:click={saveSong}>Save</Button>
<button on:click={transposeSong}>Transpose</button><input type="number" id="degree" value="1" />
<button on:click="{startScrolling}">start</button>
<button on:click="{toggleScrolling}">pause / unpause</button>
<button on:click="{stopScrolling}">stop</button>
<button on:click={()=>updateFontSize('+')}>+</button>
<button on:click={()=>updateFontSize('-')}>-</button>
