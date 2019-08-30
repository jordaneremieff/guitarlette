<script>
    
    import { onMount } from "svelte";
    import ReconnectingWebSocket from 'reconnecting-websocket';


    let data = {"title": "untitled", "artist": "nobody", "content": "", "html": ""};
    let scroller = null;
    let scrollPaused = false;

    const ws = new ReconnectingWebSocket('ws://localhost:8000/ws');
    ws.onmessage = function(msg) {
        const message = JSON.parse(msg.data);
        if (message.type === "song.detail") {
            data.title = message.title;
            data.artist = message.artist;
            data.content = message.content;
            data.html = message.html;
        } 
        if (message.type === "song.created") {
            let id = message.id;
            window.location.replace(`http://localhost:5000/composer/${id}`);
        }
        if (message.type == "song.transposed") {
            data.content = message.content;
            data.html = message.html;
        }
    }

    export let id = null;
    if (id !== null) {
        onMount(async function() {
            ws.addEventListener("open", () => {
                ws.send(JSON.stringify({"type": "song.detail", "id": id}));
            });
        });
    }

    function createSong() {
        const form = document.getElementById('editor-form');
        ws.send(JSON.stringify({
            "type": "song.create",
            "id": id,
            "title": form.title.value,
            "artist": form.artist.value,
            "content":form.content.value
        }));
    }

    function updateSong() {
        const form = document.getElementById('editor-form')
        ws.send(JSON.stringify({
            "type": "song.update",
            "id": id,
            "title": form.title.value,
            "artist": form.artist.value,
            "content":form.content.value
        }));
    }

    function deleteSong() {
        ws.send(JSON.stringify({
            "type": "song.delete",
            "id": id
        }));
    }

    async function transposeSong() {
        const degree = document.getElementById("degree").value;
        const form = document.getElementById('editor-form');
        ws.send(JSON.stringify({
            "type": "song.transpose",
            "content":form.content.value,
            "degree": degree
        }));
    }

    function startScrolling() {
        var topPos = viewer.offsetTop;
        stopScrolling();
        scroll(topPos);
    }

    function stopScrolling() {
        clearInterval(scroller);
    }

    function toggleScrolling() {
        scrollPaused = scrollPaused ? false : true;
    }

    function scroll(topPos) {
        let viewerContent= document.getElementById("viewer-content");
        viewer.scrollTop = topPos - viewerContent.offsetTop
        scroller = setInterval(function() { 
            if(!scrollPaused) {
                viewer.scrollTop += 2
            }
        }, 1000)
    }

    function updateFontSize(op) {
        let viewerContent = document.getElementById("viewer-content");
        var fontSize = parseInt(window.getComputedStyle(viewerContent, null).getPropertyValue('font-size'));
        if (op == "-")
            fontSize -= 5;
        else
            fontSize += 5;
        viewerContent.style.fontSize = fontSize.toString()+"px";
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
    </div>
    <div id="viewer">
        <div id="viewer-controls">
            {#if id}
                <button on:click={updateSong}>Save</button>
                <button on:click={deleteSong}>Delete</button>
            {:else}
                <button on:click={createSong}>Save</button>
            {/if}
            <button on:click={deleteSong}>Delete</button>
            <button on:click={transposeSong}>Transpose</button><input type="number" id="degree" value="1" />
            <button on:click="{startScrolling}">Start / Reset</button>
            <button on:click="{toggleScrolling}">Pause / Unpause</button>
            <button on:click={()=>updateFontSize('+')}>+</button>
            <button on:click={()=>updateFontSize('-')}>-</button>
        </div>
        <div id="viewer-content">
            {@html data.html}
        </div>
    </div>
    <div id="clear"></div>
</div>