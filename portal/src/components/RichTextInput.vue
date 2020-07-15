<template>
  <div>
    <div class="header">
      <label @click="setFocus">
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
            :class="{ 'is-active': isActive.heading({ level: 3 }) }"
            @click="commands.heading({ level: 3 })"
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
    <InputLanguageWrapper :language="language">
      <editor-content
        class="editor__content"
        :class="{ 'with-language': language !== null }"
        :editor="editor"
        @onUpdate="onUpdate"
      />
    </InputLanguageWrapper>
  </div>
</template>
<script>
import { Editor, EditorContent, EditorMenuBar } from 'tiptap'
import {
  Bold,
  BulletList,
  HardBreak,
  Heading,
  History,
  Italic,
  ListItem,
  Placeholder,
  Underline
} from 'tiptap-extensions'
import InputLanguageWrapper from '~/components/InputLanguageWrapper'

export default {
  name: 'RichTextInput',
  components: {
    EditorContent,
    EditorMenuBar,
    InputLanguageWrapper
  },
  props: {
    title: {
      type: String,
      default: null
    },
    language: {
      type: String,
      default: null
    },
    value: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: ''
    },
    id: {
      type: String,
      default: null
    },
    update: {
      type: Function,
      default: () => {}
    }
  },
  data() {
    return {
      editor: new Editor({
        content: this.value,
        onUpdate: this.onUpdate,
        extensions: [
          new Placeholder({
            emptyEditorClass: 'is-editor-empty',
            emptyNodeClass: 'is-empty',
            emptyNodeText: this.placeholder,
            showOnlyWhenEditable: true,
            showOnlyCurrent: true
          }),
          new Bold(),
          new Italic(),
          new Underline(),
          new Heading({ levels: [3] }),
          new HardBreak(),
          new BulletList(),
          new ListItem(),
          new History()
        ]
      })
    }
  },
  watch: {
    value(value) {
      // Editor loses focus when setContent is called, skip it when content is the same
      if (value === this.editor.getHTML()) {
        return
      }
      this.editor.setContent(value)
    }
  },
  beforeDestroy() {
    this.editor.destroy()
  },
  methods: {
    setFocus() {
      this.editor.focus()
    },
    onUpdate(value) {
      this.$emit('input', value.getHTML())
    }
  }
}
</script>
<style>
.ProseMirror:focus {
  outline: none;
}

.editor__content p.is-editor-empty:first-child::before {
  content: attr(data-empty-text);
  float: left;
  color: #aaa;
  pointer-events: none;
  height: 0;
  font-style: italic;
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
  max-height: 300px;
  overflow-y: scroll;

  &.with-language {
    padding-left: 60px;
  }
}
</style>
