<script>
  import Tab, {Icon, Label} from '@smui/tab';
  import TabBar from '@smui/tab-bar';
  import Button from '@smui/button';
  import {Router, Route, navigate, link} from "svelte-routing";

  import Home from "./Home.svelte";
  import Composer from "./Composer.svelte";

  let url = "";
  let navTabs = [
    {
      link: "/",
      label: "Home"
    },
    {
      link: "composer",
      label: "Composer"
    }
  ];

  let activeTab = navTabs[0];

  function handleNavClick(tab) {
    activeTab = tab;
    navigate(tab.link, { replace: true });
  }
</script>

<style>
  section > div {
    margin-bottom: 40px;
  }
  .icon-indicators :global(.mdc-tab-indicator--active .mdc-tab-indicator__content) {
    opacity: .2;
  }
  a {
    text-decoration: none;
  }
</style>

<section>
  <h2>guitarlette</h2>
  <div>
    <Router url="{url}">
    <nav>
      <TabBar tabs={navTabs} let:tab bind:active={activeTab}>
        <a on:click|preventDefault={() => handleNavClick(tab)} href="{tab.link}">
        <Tab {tab} minWidth>
          <Label>{tab.label}</Label>
        </Tab>
        </a>
      </TabBar>
    </nav>
    <div>
      <Route path="/" component="{Home}" />
      <Route path="composer/:id" component="{Composer}" />
      <Route path="composer" component="{Composer}" />
    </div>
    </Router>
  </div>
</section>
