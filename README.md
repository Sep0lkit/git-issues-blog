# Git-Issues-Blog

A Github action to create issues from github repository.

I use this action for my blog system,  make me more focused on writing.

## **Features:**

- **WYWIWYG**(What You Write Is What You Get)
- based on github file content 
- Automatically generate and update issues
- Automatic conversion image link
- Easy to using

## Usage:

```
    - name: Git-Issues-Blog
      uses: Sep0lkit/git-issues-blog@v1.0
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        POSTS_PATH: 'posts'
```

#### Environment variables
- `POSTS_PATH` - blog posts folder name, default is "posts"



## License

MIT License - see the [LICENSE](LICENSE) file for details