// Plain Eleventy: Nunjucks templates in src/, built pages in ../html (committed, served by nginx).
export default function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy("src/assets");
  return {
    dir: { input: "src", output: "../html", includes: "_includes", data: "_data" },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
  };
}
