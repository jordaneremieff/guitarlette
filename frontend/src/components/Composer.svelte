<script>
    
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
        if (json.redirect === true) {
            let id = json.id;
            window.location.replace(`http://localhost:5000/composer/${id}`);
        } else {
            let viewerContent = document.getElementById("viewer-content");
            viewerContent.innerHTML = json.viewer_content;
        }
    }

    async function transposeSong() {
        const degree = document.getElementById("degree").value;
        const form = document.getElementById('editor-form');
        const formData = new FormData();
        formData.append("content", data.content);
        formData.append("degree", degree);
        const response = await fetch("http://localhost:8000/transpose", {
            method: "post",
            body: formData,
        })
        const json = await response.json();
        let editorContent = document.getElementById("editor-content");
        let viewerContent = document.getElementById("viewer-content");
        data.content = json.content;
        viewerContent.innerHTML = json.viewer_content;

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
                viewer.scrollTop += 20
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

:global(body) {
    font-family: monospace;
    background-color:#F5F5F5;
    color: #212121;
}

:global(.chord) {
    font-weight: bold;
}

:global(.chord-delimiter) {
    padding: 3px;
}

:global(.row) {
    margin-top: 10px;
}

#container {
    width: 100%;
    background-color: #FAFAFA;
    color: #000000;
}
#editor {
    width: 40%;
    float: left;
    height: 800px;
}

#editor-form {
    display: inline-block;
    margin: 5px;
}
textarea {
    background-color: #FFFFFF;
    width: 99%;
    margin-right: 1%;
    height: 670px;
    -webkit-box-sizing: border-box; 
    -moz-box-sizing: border-box; 
    box-sizing: border-box;
    color: #212121; 
}

#viewer {
    width: 60%;
    font-size: 18px;
    overflow-y: scroll; 
    height: 800px;
    margin-bottom: 10px;
}

#viewer-content {
    background-color: #FFFFFF;
    color: #212121;
    font-size: 10px;
    padding: 10px;
}

#viewer-controls {
    background: #FAFAFA;
    padding: 5px;
    color: #FFFFFF;
    font-size: 10px;
    position: sticky;
    top: 0;
}


#clear {
    clear: both;
}

button {
    display: inline-block;
}
</style>



<h1>Composer</h1>
<div id="container">
    <div id="editor">
        <form id="editor-form">
            <label for="title">Title</label>
            <input type="text" id="title" name="title" value="{data.title}">
            <label for="artist">Artist</label>
            <input type="text" id="artist" name="artist" value="{data.artist}">
            <label for="content">Content</label>
            <textarea rows="50" cols="100" id="content" name="content" bind:value="{data.content}"></textarea>
        </form>
        <button on:click={saveSong}>Save</button>
    </div>
    <div id="viewer">
        <div id="viewer-controls">
            
            <button on:click={transposeSong}>Transpose</button><input type="number" id="degree" value="1" />
            <button on:click="{startScrolling}">start</button>
            <button on:click="{toggleScrolling}">pause / unpause</button>
            <button on:click="{stopScrolling}">stop</button>
            <button on:click={()=>updateFontSize('+')}>+</button>
            <button on:click={()=>updateFontSize('-')}>-</button>
        </div>
        <div id="viewer-content">
            {@html data.viewer_content}
        </div>
    </div>
    <div id="clear"></div>
</div>