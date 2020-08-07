# code-tree-stats

This simple python script shows the number of files/lines grouped by file extensions without any 3rd party libraries.

### Args:

```
usage: cts.py [options]

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -c N, --cutoff N      number of elements to show
  -B, --show_binary     show binary files in the list
  -N, --hide_negligible hides files with negligible amount of lines (<00.01%)
  -A, --hide_animation  hides 'Loading...' text
```

**Minimum python version: 3.6**

<details>
  <summary>About the code</summary>
  <p>
    <b>Why is everything in a single file?</b><br>
    One of the goals I set out is to only have a single file. In the future I may move some of the classes to separate files.
  </p>
  <p>
    <b>Reinventing the wheel</b><br>
    I don't use <u>external packages</u> for a similar reason. I want it to run on any device, without any additional files.
  </p>
</details>

### License

This project is licensed under the MIT License - see the [MIT License](LICENSE) file for details.
