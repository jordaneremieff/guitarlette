<script>
    import { Router, Route } from "svelte-routing";
    import NavLink from "./components/NavLink.svelte";
    import Home from "./components/Home.svelte";
    import Composer from "./components/Composer.svelte";
    let url = "";
</script>

<Router url="{url}">
  <nav>
    <NavLink to="/">Home</NavLink>
    <NavLink to="composer">Composer</NavLink>
</nav>
<div>
    <Route path="/" component="{Home}" />
    <Route path="composer/:id" component="{Composer}" />
    <Route path="composer" component="{Composer}" />
</div>
</Router>