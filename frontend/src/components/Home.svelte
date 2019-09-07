<script>
  import { onMount } from "svelte";
  import List, {Item, Separator, Text, PrimaryText, SecondaryText} from '@smui/list';
  let data = [];
  onMount(async function() {
    const response = await fetch("http://localhost:8000/songs");
    data = await response.json();
  });
</script>

<h1>Songs</h1>
<div>
  <List>
    {#each data as song}
      <Item style="padding-bottom: 5px;">
      
        <Text>
          <a href="http://localhost:5000/composer/{song.id}"><PrimaryText>{song.title}</PrimaryText></a>
          <SecondaryText>{song.artist}</SecondaryText>
        </Text>
      </Item>
      <Separator />
    {/each}
  </List>
</div>