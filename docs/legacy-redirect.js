(() => {
  const params = new URLSearchParams(location.search);
  const slug = value => String(value || '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
    .toLowerCase().replace(/&/g, ' ').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  const route = () => {
    const page = location.pathname.split('/').pop().toLowerCase();
    if (page === 'explore.html') {
      const group = params.get('group') || params.get('category') || '';
      const subgroup = params.get('subgroup') || '';
      if (!group) return `#/explore${location.search}`;
      return fetch('./api/legacy-aliases.json').then(response => response.json()).then(aliases => {
        let target = aliases.subgroups[`${group}|${subgroup}`] || aliases.subgroups[`${Object.keys(aliases.groups).find(name => slug(name) === slug(group)) || group}|${subgroup}`];
        target ||= aliases.groups[group] || Object.entries(aliases.groups).find(([name]) => slug(name) === slug(group))?.[1] || { group, subgroup };
        const query = new URLSearchParams();
        query.set('category', slug(target.group));
        if (target.subgroup) query.set('subgroup', slug(target.subgroup));
        for (const key of ['q', 'live', 'chart', 'sort']) if (params.has(key)) query.set(key, params.get(key));
        return `#/explore?${query}`;
      }).catch(() => `#/explore?category=${encodeURIComponent(slug(group))}`);
    }
    if (page === 'indicator.html') {
      const key = params.get('id') || params.get('key') || '';
      return key ? `#/indicator/${encodeURIComponent(key)}` : '#/explore';
    }
    if (page === 'compare.html') return `#/compare${location.search}`;
    if (page === 'sources.html') return '#/sources';
    if (page === 'about.html') return '#/about';
    return '#/api';
  };
  Promise.resolve(route()).then(hash => { location.replace(`./${hash}`); });
})();
