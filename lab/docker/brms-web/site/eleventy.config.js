// Plain Eleventy: Nunjucks templates in src/, built pages in _site. The Dockerfile builds them and nginx serves them.
export default function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy("src/assets");
  return {
    dir: { input: "src", output: "_site", includes: "_includes", data: "_data" },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
  };
}
