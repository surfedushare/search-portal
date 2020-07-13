<template>
  <div>
    <div class="header">
      <label>
        {{ title }}
      </label>
      <editor-menu-bar v-slot="{ commands, isActive }" :editor="editor">
        <div class="menubar">
          <div
            class="menubar-button bold"
            :class="{ 'is-active': isActive.bold() }"
            @click="commands.bold"
          >
            <span>B</span>
          </div>
          <div
            class="menubar-button italic"
            :class="{ 'is-active': isActive.italic() }"
            @click="commands.italic"
          >
            <span>I</span>
          </div>
          <div
            class="menubar-button underline"
            :class="{ 'is-active': isActive.underline() }"
            @click="commands.underline"
          >
            <span>U</span>
          </div>
          <div
            class="menubar-button heading"
            :class="{ 'is-active': isActive.heading({ level: 1 }) }"
            @click="commands.heading({ level: 1 })"
          >
            <span>H</span>
          </div>
          <div
            class="menubar-button bullet-list"
            :class="{ 'is-active': isActive.bullet_list() }"
            @click="commands.bullet_list"
          >
            <span><i class="fas fa-list"></i></span>
          </div>
        </div>
      </editor-menu-bar>
    </div>
    <editor-content class="editor__content" :editor="editor" />
  </div>
</template>
<script>
import { Editor, EditorContent, EditorMenuBar } from 'tiptap'
import {
  Heading,
  BulletList,
  HardBreak,
  Bold,
  Italic,
  Underline,
  ListItem
} from 'tiptap-extensions'

export default {
  name: 'RichTextInput',
  components: {
    EditorContent,
    EditorMenuBar
  },
  props: {
    title: {
      type: String,
      default: null
    },
    value: {
      type: String,
      default: ''
    }
  },
  data() {
    return {
      editor: new Editor({
        content: this.value,
        extensions: [
          new Bold(),
          new Italic(),
          new Underline(),
          new Heading({ levels: [1] }),
          new HardBreak(),
          new BulletList(),
          new ListItem()
        ]
      })
    }
  },
  watch: {
    value(x) {
      this.editor.setContent(x)
    }
  }
}
</script>
<style>
.ProseMirror:focus {
  outline: none;
}
</style>
<style scoped lang="less">
.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  align-items: flex-end;

  label {
    font-weight: bold;
    color: #353535;
  }
}
.menubar {
  display: inline-block;
  border: 1px solid #e5e5e5;
  border-radius: 5px;
}
.menubar-button {
  display: inline-block;
  font-weight: 600;
  padding: 3px 0;
  cursor: pointer;

  span {
    border-right: 1px solid #e5e5e5;
    padding: 0px 10px;
    line-height: 1em;
  }

  &.is-active {
    background-color: #e5e5e5;
    margin-left: -1px;

    &:first-child {
      margin-left: 0;
    }

    span {
      border-right: 1px solid darken(#e5e5e5, 20%);
      border-left: 1px solid darken(#e5e5e5, 20%);
    }
  }

  &.is-active:first-child span {
    border-left: none;
  }

  &.is-active:last-child span {
    border-right: none;
  }

  &.bold {
    font-weight: bolder;
  }
  &.italic {
    font-style: italic;
  }
  &.underline {
    text-decoration: underline;
  }
  .fa-list {
    font-size: 0.8em;
  }
  &:last-child {
    border: none;
  }
}

.editor__content {
  border: 1px solid #e5e5e5;
  border-radius: 7px;
  padding: 10px;
}
</style>
