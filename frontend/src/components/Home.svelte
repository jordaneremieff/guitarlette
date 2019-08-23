<script>
    import { onMount } from "svelte";
    let data = [];
    onMount(async function() {
        const response = await fetch("http://localhost:8000/songs");
        const json = await response.json();
        data = json;
    });
</script>

<h1>Songs</h1>
{#each data as song}
    <ul>
        <li><a href="http://localhost:5000/composer/{song.id}">{song.title}</a></li>
    </ul>
{/each}

