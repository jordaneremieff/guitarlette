<script>
    import { onMount } from "svelte";
    let data = {"title": "", "content": ""};
    export let id = null;
    if (id !== null) {
        onMount(async function() {
            const response = await fetch(`http://localhost:8000/songs/${id}`);
            const json = await response.json();
            data = json;
        });
    }
    async function saveSong() {
        const form = document.getElementById('songForm');
        const formData = new FormData();
        let url = "";
        if (id !== null) {
            url = `http://localhost:8000/songs/${id}`;
        } else {
            url = `http://localhost:8000/songs`;
        }
        formData.append("title", form.title.value);
        formData.append("content", form.content.value);
        const response = await fetch(url, {
            method: "post",
            body: formData,
        })
        const json = await response.json();
        let composerContent = document.getElementById("composerContent");
        composerContent.innerHTML = json.content;
    }

    async function transposeSong() {
    }

    async function scrollSong() {
    }

    async function increaseFontSize() {
    }

    async function decreaseFontSize() {
    }
</script>

<style>
</style>


<h1>Composer</h1>
<form id="songForm">
    title: <input type="text" id="title" value="{data.title}">
    <br>
    content: <textarea rows="50" cols="100" id="content" value="{data.content}"></textarea>
</form>

<div id="composer">
    <div id="composerContent">{data.content}</div>
</div>

<button on:click={saveSong}>Save</button>
<button on:click={transposeSong}>Transpose</button>
<button on:click={scrollSong}>Scroll</button>
<button on:click={increaseFontSize}>+</button>
<button on:click={decreaseFontSize}>-</button>
